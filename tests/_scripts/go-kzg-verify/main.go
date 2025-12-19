package main

import (
	"crypto/ecdsa"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/rlp"
	goethkzg "github.com/crate-crypto/go-eth-kzg"
	"github.com/holiman/uint256"
	"gopkg.in/yaml.v3"
)

// TestData represents the structure of consensus-spec-tests data.yaml
type TestData struct {
	Input struct {
		Blob string `yaml:"blob"`
	} `yaml:"input"`
	Output [][]string `yaml:"output"` // [cells, proofs]
}

// OutputData represents our computed results
type OutputData struct {
	TestName             string   `json:"test_name"`
	Blob                 string   `json:"blob"`
	Commitment           string   `json:"commitment"`
	VersionedHash        string   `json:"versioned_hash"`
	CellProofs           []string `json:"cell_proofs"`
	SignedTransactionHex string   `json:"signed_transaction_hex"`
}

// BlobTxPayload represents the transaction payload fields
type BlobTxPayload struct {
	ChainID              *uint256.Int
	Nonce                uint64
	MaxPriorityFeePerGas *uint256.Int
	MaxFeePerGas         *uint256.Int
	Gas                  uint64
	To                   common.Address
	Value                *uint256.Int
	Data                 []byte
	AccessList           []interface{}
	MaxFeePerBlobGas     *uint256.Int
	BlobVersionedHashes  []common.Hash
	V                    *uint256.Int
	R                    *uint256.Int
	S                    *uint256.Int
}

func hexToBytes(hexStr string) ([]byte, error) {
	hexStr = strings.TrimPrefix(hexStr, "0x")
	return hex.DecodeString(hexStr)
}

func bytesToHex(b []byte) string {
	return "0x" + hex.EncodeToString(b)
}

// computeVersionedHash computes the versioned hash from a commitment
func computeVersionedHash(commitment goethkzg.KZGCommitment) common.Hash {
	h := sha256.Sum256(commitment[:])
	h[0] = 0x01
	return common.Hash(h)
}

func main() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <consensus-spec-tests-dir> <output-file>\n", os.Args[0])
		os.Exit(1)
	}

	testDir := os.Args[1]
	outputFile := os.Args[2]

	// Initialize go-eth-kzg context for EIP-7594
	ctx, err := goethkzg.NewContext4096Secure()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to create KZG context: %v\n", err)
		os.Exit(1)
	}

	// Private key used in eth-account tests
	privateKeyHex := "4646464646464646464646464646464646464646464646464646464646464646"
	privateKey, err := crypto.HexToECDSA(privateKeyHex)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to parse private key: %v\n", err)
		os.Exit(1)
	}

	publicKey := privateKey.Public()
	publicKeyECDSA, ok := publicKey.(*ecdsa.PublicKey)
	if !ok {
		fmt.Fprintf(os.Stderr, "Failed to get public key\n")
		os.Exit(1)
	}
	fromAddress := crypto.PubkeyToAddress(*publicKeyECDSA)
	fmt.Printf("Signing address: %s\n", fromAddress.Hex())

	// Find all valid test cases
	pattern := filepath.Join(testDir, "*_valid_*", "data.yaml")
	matches, err := filepath.Glob(pattern)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to glob pattern: %v\n", err)
		os.Exit(1)
	}

	if len(matches) == 0 {
		fmt.Fprintf(os.Stderr, "No test files found matching pattern: %s\n", pattern)
		os.Exit(1)
	}

	fmt.Printf("Found %d test files\n", len(matches))

	var results []OutputData

	for _, testFile := range matches {
		testName := filepath.Base(filepath.Dir(testFile))
		fmt.Printf("Processing: %s\n", testName)

		// Read test data
		data, err := os.ReadFile(testFile)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to read %s: %v\n", testFile, err)
			continue
		}

		var testData TestData
		if err := yaml.Unmarshal(data, &testData); err != nil {
			fmt.Fprintf(os.Stderr, "Failed to parse %s: %v\n", testFile, err)
			continue
		}

		// Convert blob from hex
		blobBytes, err := hexToBytes(testData.Input.Blob)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to decode blob hex in %s: %v\n", testFile, err)
			continue
		}

		// Create blob for go-eth-kzg
		var blob goethkzg.Blob
		copy(blob[:], blobBytes)

		// Compute commitment using go-eth-kzg
		commitment, err := ctx.BlobToKZGCommitment(&blob, 1)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to compute commitment for %s: %v\n", testFile, err)
			continue
		}

		// Compute cells and cell proofs using go-eth-kzg (EIP-7594)
		cells, cellProofs, err := ctx.ComputeCellsAndKZGProofs(&blob, 1)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to compute cell proofs for %s: %v\n", testFile, err)
			continue
		}

		// Convert cell proofs to hex strings
		cellProofsHex := make([]string, len(cellProofs))
		for i, proof := range cellProofs {
			cellProofsHex[i] = bytesToHex(proof[:])
		}

		// Compute versioned hash
		versionedHash := computeVersionedHash(commitment)

		// Create EIP-7594 format transaction
		toAddr := common.HexToAddress("0x45Ae5777c9b35Eb16280e423b0d7c91C06C66B58")
		txData, _ := hex.DecodeString("52fdfc072182654f")

		// Build the unsigned transaction payload
		txPayload := &BlobTxPayload{
			ChainID:              uint256.NewInt(1),
			Nonce:                1,
			MaxPriorityFeePerGas: uint256.NewInt(50),
			MaxFeePerGas:         uint256.NewInt(1000),
			Gas:                  100000,
			To:                   toAddr,
			Value:                uint256.NewInt(1),
			Data:                 txData,
			AccessList:           []interface{}{},
			MaxFeePerBlobGas:     uint256.NewInt(100),
			BlobVersionedHashes:  []common.Hash{versionedHash},
		}

		// Encode unsigned transaction for signing
		unsignedTxRLP := encodeUnsignedBlobTx(txPayload)

		// Compute hash to sign: keccak256(0x03 || rlp([...]))
		txHash := crypto.Keccak256(append([]byte{0x03}, unsignedTxRLP...))

		// Sign the hash
		sig, err := crypto.Sign(txHash, privateKey)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Failed to sign transaction for %s: %v\n", testFile, err)
			continue
		}

		// Extract v, r, s from signature
		r := new(uint256.Int).SetBytes(sig[:32])
		s := new(uint256.Int).SetBytes(sig[32:64])
		v := new(uint256.Int).SetUint64(uint64(sig[64]))

		txPayload.V = v
		txPayload.R = r
		txPayload.S = s

		// Encode the full EIP-7594 transaction
		// Format: 0x03 || rlp([tx_payload_body, wrapper_version, blobs, commitments, cell_proofs])
		signedTxBytes := encodeSignedBlobTxEIP7594(txPayload, blob, commitment, cells, cellProofs)

		result := OutputData{
			TestName:             testName,
			Blob:                 testData.Input.Blob,
			Commitment:           bytesToHex(commitment[:]),
			VersionedHash:        bytesToHex(versionedHash[:]),
			CellProofs:           cellProofsHex,
			SignedTransactionHex: bytesToHex(signedTxBytes),
		}

		results = append(results, result)
		fmt.Printf("  ✓ Signed transaction: %d bytes, %d cell proofs\n", len(signedTxBytes), len(cellProofs))
	}

	// Write results to output file
	outputData, err := json.MarshalIndent(results, "", "  ")
	if err != nil {
		fmt.Fprintf(os.Stderr, "Failed to marshal results: %v\n", err)
		os.Exit(1)
	}

	if err := os.WriteFile(outputFile, outputData, 0644); err != nil {
		fmt.Fprintf(os.Stderr, "Failed to write output file: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("\nResults written to: %s\n", outputFile)
}

// encodeUnsignedBlobTx encodes the unsigned transaction fields for signing
func encodeUnsignedBlobTx(tx *BlobTxPayload) []byte {
	fields := []interface{}{
		tx.ChainID.ToBig(),
		tx.Nonce,
		tx.MaxPriorityFeePerGas.ToBig(),
		tx.MaxFeePerGas.ToBig(),
		tx.Gas,
		tx.To.Bytes(),
		tx.Value.ToBig(),
		tx.Data,
		tx.AccessList,
		tx.MaxFeePerBlobGas.ToBig(),
		tx.BlobVersionedHashes,
	}
	encoded, _ := rlp.EncodeToBytes(fields)
	return encoded
}

// encodeSignedBlobTxEIP7594 encodes the signed transaction in EIP-7594 format
func encodeSignedBlobTxEIP7594(tx *BlobTxPayload, blob goethkzg.Blob, commitment goethkzg.KZGCommitment, cells [goethkzg.CellsPerExtBlob]*goethkzg.Cell, cellProofs [goethkzg.CellsPerExtBlob]goethkzg.KZGProof) []byte {
	// tx_payload_body fields
	txPayloadBody := []interface{}{
		tx.ChainID.ToBig(),
		tx.Nonce,
		tx.MaxPriorityFeePerGas.ToBig(),
		tx.MaxFeePerGas.ToBig(),
		tx.Gas,
		tx.To.Bytes(),
		tx.Value.ToBig(),
		tx.Data,
		tx.AccessList,
		tx.MaxFeePerBlobGas.ToBig(),
		tx.BlobVersionedHashes,
		tx.V.ToBig(),
		tx.R.ToBig(),
		tx.S.ToBig(),
	}

	// Convert cell proofs to byte slices
	cellProofsBytes := make([][]byte, len(cellProofs))
	for i, proof := range cellProofs {
		cellProofsBytes[i] = proof[:]
	}

	// EIP-7594 format: [tx_payload_body, wrapper_version, blobs, commitments, cell_proofs]
	pooledTx := []interface{}{
		txPayloadBody,
		uint64(1), // wrapper_version = 1
		[][]byte{blob[:]},
		[][]byte{commitment[:]},
		cellProofsBytes,
	}

	encoded, _ := rlp.EncodeToBytes(pooledTx)

	// Prepend transaction type (0x03)
	return append([]byte{0x03}, encoded...)
}

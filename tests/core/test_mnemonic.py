# Originally from: https://github.com/trezor/python-mnemonic
#
# Copyright (c) 2013 Pavol Rusnak
# Copyright (c) 2017 mruddy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import pytest

from eth_account.hdaccount.mnemonic import (
    Mnemonic,
    ValidationError,
    normalize_string,
)


def test_failed_checksum():
    mnemo = Mnemonic("english")
    assert not mnemo.is_mnemonic_valid(
        "bless cloud wheel regular tiny venue bird web grief security dignity zoo"
    )


@pytest.mark.parametrize(
    "language,word",
    [
        ("english", "security"),
        ("french", "baguette"),
        ("spanish", "leche"),
        ("italian", "cordata"),
        ("czech", "nitro"),
        ("japanese", "あらためる"),
        ("korean", "강북"),
        (
            "chinese_simplified",
            "也",  # NOTE: This succeeds even though this character is in both
        ),
        (
            "chinese_traditional",
            "滅",  # traditional and simplified Chinese, assumes simplified
        ),
    ],
)
def test_detection(language, word):
    assert language == Mnemonic.detect_language(word)


def test_undetected_language():
    with pytest.raises(ValidationError):
        Mnemonic.detect_language("xxxxxxx")
    with pytest.raises(ValidationError):
        Mnemonic("xxxxxxx")


def test_expand_word():
    m = Mnemonic("english")
    assert "" == m.expand_word("")
    assert " " == m.expand_word(" ")
    assert "access" == m.expand_word("access")  # word in list
    assert "access" == m.expand_word("acce")  # unique prefix expanded to word in list
    assert "acb" == m.expand_word("acb")  # not found at all
    assert "acc" == m.expand_word("acc")  # multi-prefix match
    assert "act" == m.expand_word("act")  # exact three letter match
    assert "action" == m.expand_word("acti")  # unique prefix expanded to word in list


@pytest.mark.parametrize(
    "lang",
    {
        lang
        for lang in Mnemonic.list_languages()
        if lang
        not in (
            # These languages can't support word expansion
            "japanese",
            "korean",
            "chinese_simplified",
            "chinese_traditional",
        )
    },
)
def test_expand(lang):
    m = Mnemonic(lang)
    # Generates a random set of words, so will never be the same set of words
    words = m.generate()
    for word in words.split(" "):  # Space delinates in languages not excluded above
        # BIP39 can support word expansion with as little as 4 characters
        norm_word = normalize_string(word)
        for size in range(4, len(norm_word)):
            assert m.expand(norm_word[: size + 1]) == word


@pytest.mark.parametrize("lang", Mnemonic.list_languages())
@pytest.mark.parametrize("num_words", [12, 15, 18, 21, 24])
def test_generation(lang, num_words):
    m = Mnemonic(lang)
    mnemonic = m.generate(num_words)
    assert m.is_mnemonic_valid(mnemonic)
    # NOTE: Sometimes traditional chinese can return characters that are also
    # valid simplified chinese characters. In that scenario, the detection
    # algorithm will assume simplified.
    if lang == "chinese_traditional":
        assert "chinese" in Mnemonic.detect_language(mnemonic)
    else:
        assert Mnemonic.detect_language(mnemonic) == lang
    assert len(Mnemonic.to_seed(mnemonic)) == 64


@pytest.mark.parametrize(
    "entropy,expected_mnemonic,expected_seed",
    [
        (
            "00000000000000000000000000000000",
            "abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon about",
            "c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e5349553"
            "1f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04",
        ),
        (
            "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
            "legal winner thank year wave sausage "
            "worth useful legal winner thank yellow",
            "2e8905819b8723fe2c1d161860e5ee1830318dbf49a83bd451cfb8440c28bd6f"
            "a457fe1296106559a3c80937a1c1069be3a3a5bd381ee6260e8d9739fce1f607",
        ),
        (
            "80808080808080808080808080808080",
            "letter advice cage absurd amount doctor "
            "acoustic avoid letter advice cage above",
            "d71de856f81a8acc65e6fc851a38d4d7ec216fd0796d0a6827a3ad6ed5511a30"
            "fa280f12eb2e47ed2ac03b5c462a0358d18d69fe4f985ec81778c1b370b652a8",
        ),
        (
            "ffffffffffffffffffffffffffffffff",
            "zoo zoo zoo zoo zoo zoo " "zoo zoo zoo zoo zoo wrong",
            "ac27495480225222079d7be181583751e86f571027b0497b5b5d11218e0a8a13"
            "332572917f0f8e5a589620c6f15b11c61dee327651a14c34e18231052e48c069",
        ),
        (
            "000000000000000000000000000000000000000000000000",
            "abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon agent",
            "035895f2f481b1b0f01fcf8c289c794660b289981a78f8106447707fdd9666ca"
            "06da5a9a565181599b79f53b844d8a71dd9f439c52a3d7b3e8a79c906ac845fa",
        ),
        (
            "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
            "legal winner thank year wave sausage "
            "worth useful legal winner thank year "
            "wave sausage worth useful legal will",
            "f2b94508732bcbacbcc020faefecfc89feafa6649a5491b8c952cede496c214a"
            "0c7b3c392d168748f2d4a612bada0753b52a1c7ac53c1e93abd5c6320b9e95dd",
        ),
        (
            "808080808080808080808080808080808080808080808080",
            "letter advice cage absurd amount doctor "
            "acoustic avoid letter advice cage absurd "
            "amount doctor acoustic avoid letter always",
            "107d7c02a5aa6f38c58083ff74f04c607c2d2c0ecc55501dadd72d025b751bc2"
            "7fe913ffb796f841c49b1d33b610cf0e91d3aa239027f5e99fe4ce9e5088cd65",
        ),
        (
            "ffffffffffffffffffffffffffffffffffffffffffffffff",
            "zoo zoo zoo zoo zoo zoo "
            "zoo zoo zoo zoo zoo zoo "
            "zoo zoo zoo zoo zoo when",
            "0cd6e5d827bb62eb8fc1e262254223817fd068a74b5b449cc2f667c3f1f985a7"
            "6379b43348d952e2265b4cd129090758b3e3c2c49103b5051aac2eaeb890a528",
        ),
        (
            "0000000000000000000000000000000000000000000000000000000000000000",
            "abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon abandon "
            "abandon abandon abandon abandon abandon art",
            "bda85446c68413707090a52022edd26a1c9462295029f2e60cd7c4f2bbd30971"
            "70af7a4d73245cafa9c3cca8d561a7c3de6f5d4a10be8ed2a5e608d68f92fcc8",
        ),
        (
            "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
            "legal winner thank year wave sausage "
            "worth useful legal winner thank year "
            "wave sausage worth useful legal winner "
            "thank year wave sausage worth title",
            "bc09fca1804f7e69da93c2f2028eb238c227f2e9dda30cd63699232578480a40"
            "21b146ad717fbb7e451ce9eb835f43620bf5c514db0f8add49f5d121449d3e87",
        ),
        (
            "8080808080808080808080808080808080808080808080808080808080808080",
            "letter advice cage absurd amount doctor "
            "acoustic avoid letter advice cage absurd "
            "amount doctor acoustic avoid letter advice "
            "cage absurd amount doctor acoustic bless",
            "c0c519bd0e91a2ed54357d9d1ebef6f5af218a153624cf4f2da911a0ed8f7a09"
            "e2ef61af0aca007096df430022f7a2b6fb91661a9589097069720d015e4e982f",
        ),
        (
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "zoo zoo zoo zoo zoo zoo "
            "zoo zoo zoo zoo zoo zoo "
            "zoo zoo zoo zoo zoo zoo "
            "zoo zoo zoo zoo zoo vote",
            "dd48c104698c30cfe2b6142103248622fb7bb0ff692eebb00089b32d22484e16"
            "13912f0a5b694407be899ffd31ed3992c456cdf60f5d4564b8ba3f05a69890ad",
        ),
        (
            "9e885d952ad362caeb4efe34a8e91bd2",
            "ozone drill grab fiber curtain grace "
            "pudding thank cruise elder eight picnic",
            "274ddc525802f7c828d8ef7ddbcdc5304e87ac3535913611fbbfa986d0c9e547"
            "6c91689f9c8a54fd55bd38606aa6a8595ad213d4c9c9f9aca3fb217069a41028",
        ),
        (
            "6610b25967cdcca9d59875f5cb50b0ea75433311869e930b",
            "gravity machine north sort system female "
            "filter attitude volume fold club stay "
            "feature office ecology stable narrow fog",
            "628c3827a8823298ee685db84f55caa34b5cc195a778e52d45f59bcf75aba68e"
            "4d7590e101dc414bc1bbd5737666fbbef35d1f1903953b66624f910feef245ac",
        ),
        (
            "68a79eaca2324873eacc50cb9c6eca8cc68ea5d936f98787c60c7ebc74e6ce7c",
            "hamster diagram private dutch cause delay "
            "private meat slide toddler razor book "
            "happy fancy gospel tennis maple dilemma "
            "loan word shrug inflict delay length",
            "64c87cde7e12ecf6704ab95bb1408bef047c22db4cc7491c4271d170a1b213d2"
            "0b385bc1588d9c7b38f1b39d415665b8a9030c9ec653d75e65f847d8fc1fc440",
        ),
        (
            "c0ba5a8e914111210f2bd131f3d5e08d",
            "scheme spot photo card baby mountain "
            "device kick cradle pact join borrow",
            "ea725895aaae8d4c1cf682c1bfd2d358d52ed9f0f0591131b559e2724bb234fc"
            "a05aa9c02c57407e04ee9dc3b454aa63fbff483a8b11de949624b9f1831a9612",
        ),
        (
            "6d9be1ee6ebd27a258115aad99b7317b9c8d28b6d76431c3",
            "horn tenant knee talent sponsor spell "
            "gate clip pulse soap slush warm "
            "silver nephew swap uncle crack brave",
            "fd579828af3da1d32544ce4db5c73d53fc8acc4ddb1e3b251a31179cdb71e853"
            "c56d2fcb11aed39898ce6c34b10b5382772db8796e52837b54468aeb312cfc3d",
        ),
        (
            "9f6a2878b2520799a44ef18bc7df394e7061a224d2c33cd015b157d746869863",
            "panda eyebrow bullet gorilla call smoke "
            "muffin taste mesh discover soft ostrich "
            "alcohol speed nation flash devote level "
            "hobby quick inner drive ghost inside",
            "72be8e052fc4919d2adf28d5306b5474b0069df35b02303de8c1729c9538dbb6"
            "fc2d731d5f832193cd9fb6aeecbc469594a70e3dd50811b5067f3b88b28c3e8d",
        ),
        (
            "23db8160a31d3e0dca3688ed941adbf3",
            "cat swing flag economy stadium alone "
            "churn speed unique patch report train",
            "deb5f45449e615feff5640f2e49f933ff51895de3b4381832b3139941c57b592"
            "05a42480c52175b6efcffaa58a2503887c1e8b363a707256bdd2b587b46541f5",
        ),
        (
            "8197a4a47f0425faeaa69deebc05ca29c0a5b5cc76ceacc0",
            "light rule cinnamon wrap drastic word "
            "pride squirrel upgrade then income fatal "
            "apart sustain crack supply proud access",
            "4cbdff1ca2db800fd61cae72a57475fdc6bab03e441fd63f96dabd1f183ef5b7"
            "82925f00105f318309a7e9c3ea6967c7801e46c8a58082674c860a37b93eda02",
        ),
        (
            "066dca1a2bb7e8a1db2832148ce9933eea0f3ac9548d793112d9a95c9407efad",
            "all hour make first leader extend "
            "hole alien behind guard gospel lava "
            "path output census museum junior mass "
            "reopen famous sing advance salt reform",
            "26e975ec644423f4a4c4f4215ef09b4bd7ef924e85d1d17c4cf3f136c2863cf6"
            "df0a475045652c57eb5fb41513ca2a2d67722b77e954b4b3fc11f7590449191d",
        ),
        (
            "f30f8c1da665478f49b001d94c5fc452",
            "vessel ladder alter error federal sibling "
            "chat ability sun glass valve picture",
            "2aaa9242daafcee6aa9d7269f17d4efe271e1b9a529178d7dc139cd18747090b"
            "f9d60295d0ce74309a78852a9caadf0af48aae1c6253839624076224374bc63f",
        ),
        (
            "c10ec20dc3cd9f652c7fac2f1230f7a3c828389a14392f05",
            "scissors invite lock maple supreme raw "
            "rapid void congress muscle digital elegant "
            "little brisk hair mango congress clump",
            "7b4a10be9d98e6cba265566db7f136718e1398c71cb581e1b2f464cac1ceedf4"
            "f3e274dc270003c670ad8d02c4558b2f8e39edea2775c9e232c7cb798b069e88",
        ),
        (
            "f585c11aec520db57dd353c69554b21a89b20fb0650966fa0a9d6f74fd989d8f",
            "void come effort suffer camp survey "
            "warrior heavy shoot primary clutch crush "
            "open amazing screen patrol group space "
            "point ten exist slush involve unfold",
            "01f5bced59dec48e362f2c45b5de68b9fd6c92c6634f44d6d40aab69056506f0"
            "e35524a518034ddc1192e1dacd32c1ed3eaa3c3b131c88ed8e7e54c49a5d0998",
        ),
    ],
)
def test_english_mnemonics(entropy, expected_mnemonic, expected_seed):
    m = Mnemonic("english")
    mnemonic = m.to_mnemonic(bytes.fromhex(entropy))
    assert m.is_mnemonic_valid(mnemonic)
    assert mnemonic == expected_mnemonic

    seed = Mnemonic.to_seed(mnemonic, passphrase="TREZOR")
    assert seed.hex() == expected_seed


@pytest.mark.parametrize(
    "entropy,expected_mnemonic,passphrase,expected_seed",
    [
        (
            "00000000000000000000000000000000",
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　"
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あおぞら",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "a262d6fb6122ecf45be09c50492b31f92e9beb7d9a845987a02cefda57a15f9c"
            "467a17872029a9e92299b5cbdf306e3a0ee620245cbd508959b6cb7ca637bd55",
        ),
        (
            "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
            "そつう　れきだい　ほんやく　わかす　りくつ　ばいか　" "ろせん　やちん　そつう　れきだい　ほんやく　わかめ",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "aee025cbe6ca256862f889e48110a6a382365142f7d16f2b9545285b3af64e54"
            "2143a577e9c144e101a6bdca18f8d97ec3366ebf5b088b1c1af9bc31346e60d9",
        ),
        (
            "80808080808080808080808080808080",
            "そとづら　あまど　おおう　あこがれる　いくぶん　けいけん　" "あたえる　いよく　そとづら　あまど　おおう　あかちゃん",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "e51736736ebdf77eda23fa17e31475fa1d9509c78f1deb6b4aacfbd760a7e2ad"
            "769c714352c95143b5c1241985bcb407df36d64e75dd5a2b78ca5d2ba82a3544",
        ),
        (
            "ffffffffffffffffffffffffffffffff",
            "われる　われる　われる　われる　われる　われる　" "われる　われる　われる　われる　われる　ろんぶん",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "4cd2ef49b479af5e1efbbd1e0bdc117f6a29b1010211df4f78e2ed4008286579"
            "3e57949236c43b9fe591ec70e5bb4298b8b71dc4b267bb96ed4ed282c8f7761c",
        ),
        (
            "000000000000000000000000000000000000000000000000",
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　"
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　"
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あらいぐま",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "d99e8f1ce2d4288d30b9c815ae981edd923c01aa4ffdc5dee1ab5fe0d4a3e139"
            "66023324d119105aff266dac32e5cd11431eeca23bbd7202ff423f30d6776d69",
        ),
        (
            "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
            "そつう　れきだい　ほんやく　わかす　りくつ　ばいか　"
            "ろせん　やちん　そつう　れきだい　ほんやく　わかす　"
            "りくつ　ばいか　ろせん　やちん　そつう　れいぎ",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "eaaf171efa5de4838c758a93d6c86d2677d4ccda4a064a7136344e975f91fe61"
            "340ec8a615464b461d67baaf12b62ab5e742f944c7bd4ab6c341fbafba435716",
        ),
        (
            "808080808080808080808080808080808080808080808080",
            "そとづら　あまど　おおう　あこがれる　いくぶん　けいけん　"
            "あたえる　いよく　そとづら　あまど　おおう　あこがれる　"
            "いくぶん　けいけん　あたえる　いよく　そとづら　いきなり",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "aec0f8d3167a10683374c222e6e632f2940c0826587ea0a73ac5d0493b6a6325"
            "90179a6538287641a9fc9df8e6f24e01bf1be548e1f74fd7407ccd72ecebe425",
        ),
        (
            "ffffffffffffffffffffffffffffffffffffffffffffffff",
            "われる　われる　われる　われる　われる　われる　"
            "われる　われる　われる　われる　われる　われる　"
            "われる　われる　われる　われる　われる　りんご",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "f0f738128a65b8d1854d68de50ed97ac1831fc3a978c569e415bbcb431a6a671"
            "d4377e3b56abd518daa861676c4da75a19ccb41e00c37d086941e471a4374b95",
        ),
        (
            "0000000000000000000000000000000000000000000000000000000000000000",
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　"
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　"
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　"
            "あいこくしん　あいこくしん　あいこくしん　あいこくしん　あいこくしん　いってい",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "23f500eec4a563bf90cfda87b3e590b211b959985c555d17e88f46f7183590cd"
            "5793458b094a4dccc8f05807ec7bd2d19ce269e20568936a751f6f1ec7c14ddd",
        ),
        (
            "7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f",
            "そつう　れきだい　ほんやく　わかす　りくつ　ばいか　"
            "ろせん　やちん　そつう　れきだい　ほんやく　わかす　"
            "りくつ　ばいか　ろせん　やちん　そつう　れきだい　"
            "ほんやく　わかす　りくつ　ばいか　ろせん　まんきつ",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "cd354a40aa2e241e8f306b3b752781b70dfd1c69190e510bc1297a9c5738e833"
            "bcdc179e81707d57263fb7564466f73d30bf979725ff783fb3eb4baa86560b05",
        ),
        (
            "8080808080808080808080808080808080808080808080808080808080808080",
            "そとづら　あまど　おおう　あこがれる　いくぶん　けいけん　"
            "あたえる　いよく　そとづら　あまど　おおう　あこがれる　"
            "いくぶん　けいけん　あたえる　いよく　そとづら　あまど　"
            "おおう　あこがれる　いくぶん　けいけん　あたえる　うめる",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "6b7cd1b2cdfeeef8615077cadd6a0625f417f287652991c80206dbd82db17bf3"
            "17d5c50a80bd9edd836b39daa1b6973359944c46d3fcc0129198dc7dc5cd0e68",
        ),
        (
            "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff",
            "われる　われる　われる　われる　われる　われる　"
            "われる　われる　われる　われる　われる　われる　"
            "われる　われる　われる　われる　われる　われる　"
            "われる　われる　われる　われる　われる　らいう",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "a44ba7054ac2f9226929d56505a51e13acdaa8a9097923ca07ea465c4c7e294c"
            "038f3f4e7e4b373726ba0057191aced6e48ac8d183f3a11569c426f0de414623",
        ),
        (
            "77c2b00716cec7213839159e404db50d",
            "せまい　うちがわ　あずき　かろう　めずらしい　だんち　" "ますく　おさめる　ていぼう　あたる　すあな　えしゃく",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "344cef9efc37d0cb36d89def03d09144dd51167923487eec42c487f742890854"
            "6fa31a3c26b7391a2b3afe7db81b9f8c5007336b58e269ea0bd10749a87e0193",
        ),
        (
            "b63a9c59a6e641f288ebc103017f1da9f8290b3da6bdef7b",
            "ぬすむ　ふっかつ　うどん　こうりつ　しつじ　りょうり　"
            "おたがい　せもたれ　あつめる　いちりゅう　はんしゃ　ごますり　"
            "そんけい　たいちょう　らしんばん　ぶんせき　やすみ　ほいく",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "b14e7d35904cb8569af0d6a016cee7066335a21c1c67891b01b83033cadb3e8a"
            "034a726e3909139ecd8b2eb9e9b05245684558f329b38480e262c1d6bc20ecc4",
        ),
        (
            "3e141609b97933b66a060dcddc71fad1d91677db872031e85f4c015c5e7e8982",
            "くのう　てぬぐい　そんかい　すろっと　ちきゅう　ほあん　"
            "とさか　はくしゅ　ひびく　みえる　そざい　てんすう　"
            "たんぴん　くしょう　すいようび　みけん　きさらぎ　げざん　"
            "ふくざつ　あつかう　はやい　くろう　おやゆび　こすう",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "32e78dce2aff5db25aa7a4a32b493b5d10b4089923f3320c8b287a77e5124554"
            "43298351beb3f7eb2390c4662a2e566eec5217e1a37467af43b46668d515e41b",
        ),
        (
            "0460ef47585604c5660618db2e6a7e7f",
            "あみもの　いきおい　ふいうち　にげる　ざんしょ　じかん　" "ついか　はたん　ほあん　すんぽう　てちがい　わかめ",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "0acf902cd391e30f3f5cb0605d72a4c849342f62bd6a360298c7013d714d7e58"
            "ddf9c7fdf141d0949f17a2c9c37ced1d8cb2edabab97c4199b142c829850154b",
        ),
        (
            "72f60ebac5dd8add8d2a25a797102c3ce21bc029c200076f",
            "すろっと　にくしみ　なやむ　たとえる　へいこう　すくう　"
            "きない　けってい　とくべつ　ねっしん　いたみ　せんせい　"
            "おくりがな　まかい　とくい　けあな　いきおい　そそぐ",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "9869e220bec09b6f0c0011f46e1f9032b269f096344028f5006a6e69ea5b0b8a"
            "fabbb6944a23e11ebd021f182dd056d96e4e3657df241ca40babda532d364f73",
        ),
        (
            "2c85efc7f24ee4573d2b81a6ec66cee209b2dcbd09d8eddc51e0215b0b68e416",
            "かほご　きうい　ゆたか　みすえる　もらう　がっこう　"
            "よそう　ずっと　ときどき　したうけ　にんか　はっこう　"
            "つみき　すうじつ　よけい　くげん　もくてき　まわり　"
            "せめる　げざい　にげる　にんたい　たんそく　ほそく",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "713b7e70c9fbc18c831bfd1f03302422822c3727a93a5efb9659bec6ad8d6f2c"
            "1b5c8ed8b0b77775feaf606e9d1cc0a84ac416a85514ad59f5541ff5e0382481",
        ),
        (
            "eaebabb2383351fd31d703840b32e9e2",
            "めいえん　さのう　めだつ　すてる　きぬごし　ろんぱ　" "はんこ　まける　たいおう　さかいし　ねんいり　はぶらし",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "06e1d5289a97bcc95cb4a6360719131a786aba057d8efd603a547bd254261c2a"
            "97fcd3e8a4e766d5416437e956b388336d36c7ad2dba4ee6796f0249b10ee961",
        ),
        (
            "7ac45cfe7722ee6c7ba84fbc2d5bd61b45cb2fe5eb65aa78",
            "せんぱい　おしえる　ぐんかん　もらう　きあい　きぼう　"
            "やおや　いせえび　のいず　じゅしん　よゆう　きみつ　"
            "さといも　ちんもく　ちわわ　しんせいじ　とめる　はちみつ",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "1fef28785d08cbf41d7a20a3a6891043395779ed74503a5652760ee8c24dfe60"
            "972105ee71d5168071a35ab7b5bd2f8831f75488078a90f0926c8e9171b2bc4a",
        ),
        (
            "4fa1a8bc3e6d80ee1316050e862c1812031493212b7ec3f3bb1b08f168cabeef",
            "こころ　いどう　きあつ　そうがんきょう　へいあん　せつりつ　"
            "ごうせい　はいち　いびき　きこく　あんい　おちつく　"
            "きこえる　けんとう　たいこ　すすめる　はっけん　ていど　"
            "はんおん　いんさつ　うなぎ　しねま　れいぼう　みつかる",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "43de99b502e152d4c198542624511db3007c8f8f126a30818e856b2d8a20400d"
            "29e7a7e3fdd21f909e23be5e3c8d9aee3a739b0b65041ff0b8637276703f65c2",
        ),
        (
            "18ab19a9f54a9274f03e5209a2ac8a91",
            "うりきれ　さいせい　じゆう　むろん　とどける　ぐうたら　" "はいれつ　ひけつ　いずれ　うちあわせ　おさめる　おたく",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "3d711f075ee44d8b535bb4561ad76d7d5350ea0b1f5d2eac054e869ff7963cdc"
            "e9581097a477d697a2a9433a0c6884bea10a2193647677977c9820dd0921cbde",
        ),
        (
            "18a2e1d81b8ecfb2a333adcb0c17a5b9eb76cc5d05db91a4",
            "うりきれ　うねる　せっさたくま　きもち　めんきょ　へいたく　"
            "たまご　ぜっく　びじゅつかん　さんそ　むせる　せいじ　"
            "ねくたい　しはらい　せおう　ねんど　たんまつ　がいけん",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "753ec9e333e616e9471482b4b70a18d413241f1e335c65cd7996f32b66cf9554"
            "6612c51dcf12ead6f805f9ee3d965846b894ae99b24204954be80810d292fcdd",
        ),
        (
            "15da872c95a13dd738fbf50e427583ad61f18fd99f628c417a61cf8343c90419",
            "うちゅう　ふそく　ひしょ　がちょう　うけもつ　めいそう　"
            "みかん　そざい　いばる　うけとる　さんま　さこつ　"
            "おうさま　ぱんつ　しひょう　めした　たはつ　いちぶ　"
            "つうじょう　てさぎょう　きつね　みすえる　いりぐち　かめれおん",
            "㍍ガバヴァぱばぐゞちぢ十人十色",
            "346b7321d8c04f6f37b49fdf062a2fddc8e1bf8f1d33171b65074531ec546d1d"
            "3469974beccb1a09263440fc92e1042580a557fdce314e27ee4eabb25fa5e5fe",
        ),
    ],
)
def test_japanese_mnemonics(entropy, expected_mnemonic, passphrase, expected_seed):
    m = Mnemonic("japanese")
    mnemonic = m.to_mnemonic(bytes.fromhex(entropy))
    assert m.is_mnemonic_valid(mnemonic)
    # NOTE For some reason, the strings weren't appearing in normalized form as
    #      copied rrom BIP39 test vectors
    assert normalize_string(mnemonic) == normalize_string(expected_mnemonic)

    seed = Mnemonic.to_seed(mnemonic, passphrase)
    assert seed.hex() == expected_seed

    # Check this because we had to normalize the string for unicode artifacts
    seed = Mnemonic.to_seed(expected_mnemonic, passphrase)
    assert seed.hex() == expected_seed

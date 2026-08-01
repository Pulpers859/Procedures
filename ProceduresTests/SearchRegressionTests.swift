import XCTest
@testable import Procedures

/// Bedside search regression suite: real clinician queries against the real
/// shipped content. If a query a clinician would type at the bedside stops
/// resolving, this fails the build. Mirrored by the Python port in
/// scripts/tests/test_search_regression.py — change both together.
@MainActor
final class SearchRegressionTests: XCTestCase {
    private static let queries: [(query: String, expectedID: String, maxRank: Int)] = [
        ("cric", "cricothyrotomy", 3),
        ("crich", "cricothyrotomy", 3),          // edit-distance-1 typo
        ("cricothyrotomy", "cricothyrotomy", 1),
        ("a-line", "arterial_line", 3),          // hyphen tokenization
        ("aline", "arterial_line", 3),
        ("abg", "arterial_line", 3),
        ("txa", "anterior_nasal_packing", 3),
        ("nosebleed", "anterior_nasal_packing", 3),
        ("epistaxis", "anterior_nasal_packing", 3),
        ("chest tube", "thoracostomy_chest_tube", 3),
        ("rsi", "endotracheal_intubation", 3),
        ("ett", "endotracheal_intubation", 3),
        ("cvc", "central_venous_catheter", 3),
        ("lp", "lumbar_puncture", 3),
        ("tamponade", "pericardiocentesis", 3),
        ("edt", "resuscitative_thoracotomy", 3),
        ("clamshell", "resuscitative_thoracotomy", 3),
        ("pigtail", "pigtail_catheter", 3),
        ("tension ptx", "needle_decompression", 3),
        ("thoracentesis", "thoracentesis", 3),
        ("thoracentsis", "thoracentesis", 3),    // edit-distance-1 typo
        ("paracentesis", "paracentesis", 3),
        ("ascites tap", "paracentesis", 3),
        ("pacer", "transvenous_pacemaker", 3),
        ("tvp", "transvenous_pacemaker", 3),
        ("usgiv", "ultrasound_guided_piv", 3),
        ("canthotomy", "lateral_canthotomy", 3),
        ("shoulder reduction", "shoulder_reduction", 3),
        ("fascia iliaca", "fascia_iliaca_block", 3),
        ("digital block", "digital_nerve_block", 3),
        ("interscalene", "block_interscalene", 3),
        ("peng", "block_peng", 3),
        ("sedation", "procedural_sedation", 3),
        // Named regional blocks must beat the generic "block" vocabulary.
        // Before the "block" synonym was narrowed these ranked 9th and 10th.
        ("tap block", "block_tap", 3),
        ("esp block", "block_thoracic_esp", 3),
        ("transversus abdominis", "block_tap", 3),
        // "tap" is overloaded: drainage taps and the TAP block share the
        // word, and both must still resolve.
        ("ascites tap", "paracentesis", 3),
        ("spinal tap", "lumbar_puncture", 3),
        ("knee tap", "knee_arthrocentesis", 3),
        // Bare clinical abbreviations clinicians actually type.
        ("io", "intraosseous_access", 3),
        ("cico", "cricothyrotomy", 3),
        ("surgical airway", "cricothyrotomy", 3),
        // "pacing" previously typo-corrected into "packing" and surfaced
        // epistaxis instead of the pacing procedure.
        ("pacing", "transvenous_pacemaker", 3)
    ]

    func testBedsideQueriesSurfaceTheExpectedProcedure() {
        let repository = ProcedureRepository()
        for entry in Self.queries {
            let results = repository.search(entry.query).map(\.id)
            guard let index = results.firstIndex(of: entry.expectedID) else {
                XCTFail("'\(entry.query)' does not surface \(entry.expectedID); top: \(results.prefix(5))")
                continue
            }
            XCTAssertLessThanOrEqual(
                index + 1, entry.maxRank,
                "'\(entry.query)' ranks \(entry.expectedID) at \(index + 1); top: \(results.prefix(5))"
            )
        }
    }

    func testBedsideQueriesMatchTheExpectedRescueCard() {
        let repository = ProcedureRepository()
        let expectations = [
            ("last", "local_anesthetic_systemic_toxicity"),
            ("lipid", "local_anesthetic_systemic_toxicity"),
            ("laryngospasm", "sedation_apnea"),
            ("capture", "failed_transvenous_capture")
        ]
        for (query, expectedID) in expectations {
            let matches = repository.searchRescueCards(query).map(\.id)
            XCTAssertTrue(matches.contains(expectedID), "'\(query)' misses rescue card \(expectedID)")
        }
    }

    /// Kit search was a strict AND across every token, so one word the kit's
    /// text happened not to contain zeroed the whole result.
    ///
    /// Counting matched tokens is not the fix on its own, and this test caught
    /// that: kit text is short and heavily shared, so "setup" — a word in the
    /// RSI, cric, and CVC checklists but not in the chest tube kit's own text
    /// — scored those three above the kit the reader actually named, and a
    /// best-tier filter then dropped the right answer entirely. Ranking on
    /// title hits first is what holds the correct kit at the top.
    func testKitSearchRanksTheNamedKitFirst() {
        let repository = ProcedureRepository()
        XCTAssertEqual(
            repository.searchKits("chest tube").first?.id, "kit_chest_tube",
            "a bare two-word query must rank the kit it names first"
        )
        XCTAssertEqual(
            repository.searchKits("chest tube setup").first?.id, "kit_chest_tube",
            "an incidental extra word must not displace the kit the reader named"
        )
        XCTAssertEqual(
            repository.searchKits("lumbar puncture tray").first?.id, "kit_lumbar_puncture"
        )
    }

    /// The flip side of not tiering: a match must never be silently dropped.
    func testKitSearchKeepsTheNamedKitEvenWithAnUnmatchedWord() {
        let repository = ProcedureRepository()
        XCTAssertTrue(
            repository.searchKits("chest tube setup").contains { $0.id == "kit_chest_tube" },
            "the named kit must survive a query word its own text does not contain"
        )
    }

    func testSynonymMapLoadsFromBundle() {
        XCTAssertFalse(ClinicalSynonyms.loadFailed, "synonyms.json must load from the app bundle")
        XCTAssertNotNil(ClinicalSynonyms.expansions["cric"], "core shorthand must survive the move to JSON")
    }

    func testHyphenatedQueriesTokenize() {
        XCTAssertEqual(ClinicalSynonyms.tokens(in: "a-line"), ["aline", "line"])
        XCTAssertEqual(ClinicalSynonyms.tokens(in: "push-dose pressor"), ["pushdose", "push", "dose", "pressor"])
    }

    func testShortShorthandIsNeverFuzzyRewritten() {
        for token in ["ij", "lp", "abg", "ptx"] {
            XCTAssertNil(ClinicalSynonyms.fuzzyMatch(for: token))
        }
    }

    func testSingleEditDefinitions() {
        XCTAssertTrue(ClinicalSynonyms.isWithinOneEdit("crich", "cric"))
        XCTAssertTrue(ClinicalSynonyms.isWithinOneEdit("cric", "crik"))
        XCTAssertFalse(ClinicalSynonyms.isWithinOneEdit("cric", "crikh"))
        XCTAssertFalse(ClinicalSynonyms.isWithinOneEdit("chest", "tube"))
    }

    func testNonsenseQueryStaysEmpty() {
        let repository = ProcedureRepository()
        XCTAssertTrue(repository.search("zzzzqqqq").isEmpty, "nonsense must not fuzzy-correct into noise")
    }

    // MARK: - Sentence queries

    /// Every query above is one or two words, which is why nothing here
    /// noticed that the procedure path kept the filler words the rescue path
    /// dropped. Scoring is substring-based, so a kept "the" matches
    /// *ca-the-ter* and "do" matches *ab-do-minal* — enough to score the whole
    /// library and bury the procedure the sentence described.
    func testFillerWordsDoNotChangeTheAnswer() {
        let repository = ProcedureRepository()
        let pairs = [
            ("chest tube", "how do i put in a chest tube"),
            ("cric", "i need to do a cric now"),
            ("central line", "the patient needs a central line"),
            ("abscess", "how do i drain an abscess"),
            ("intubation", "the patient is hypotensive after intubation")
        ]
        for (bare, sentence) in pairs {
            let bareTop = repository.search(bare).first?.id
            let sentenceTop = repository.search(sentence).first?.id
            XCTAssertNotNil(bareTop, "'\(bare)' returned nothing")
            XCTAssertEqual(sentenceTop, bareTop, "phrasing changed the answer for '\(sentence)'")
        }
    }

    // MARK: - Typo recovery scope

    /// Typo recovery is for words that are *not there*. "lost" is one edit
    /// from "last", so a query about a lost airway was rewritten into the LAST
    /// group and answered with local anaesthetic systemic toxicity, ranking
    /// nerve blocks above intubation. "pacing" → "packing" was the same bug,
    /// previously patched by narrowing one synonym rather than the class.
    func testAWordTheContentUsesIsNeverRewritten() {
        _ = ProcedureRepository()  // populates the corpus vocabulary
        for token in ["lost", "pacing", "last", "post"] {
            XCTAssertTrue(ClinicalSynonyms.corpusWords.contains(token), "\(token) should be in the corpus")
            XCTAssertNil(ClinicalSynonyms.fuzzyMatch(for: token), "\(token) is a real word, not a typo")
        }
    }

    func testGenuineMisspellingsStillRecover() {
        _ = ProcedureRepository()
        XCTAssertFalse(ClinicalSynonyms.corpusWords.contains("crich"))
        XCTAssertEqual(ClinicalSynonyms.fuzzyMatch(for: "crich"), "cric")
        XCTAssertFalse(ClinicalSynonyms.corpusWords.contains("thoracentsis"))
        XCTAssertEqual(ClinicalSynonyms.fuzzyMatch(for: "thoracentsis"), "thoracentesis")
    }

    func testALostAirwayDoesNotAnswerWithLocalAnestheticToxicity() {
        let repository = ProcedureRepository()
        let top = repository.search("lost airway").prefix(3).map(\.id)
        XCTAssertTrue(top.contains("endotracheal_intubation"), "top three: \(top)")
        XCTAssertFalse(top.contains("local_anesthetic_systemic_toxicity"), "top three: \(top)")
    }

    // MARK: - Crash vocabulary and browse order

    /// "Crashing" is the word actually said for the situation the Rescue tab
    /// exists for, and it resolved to nothing: it is in no card's text and the
    /// synonym map had no crash entry. The queries below only appeared to work
    /// because "my" and "is" were matching *my-ocardial* and *ep-is-taxis*.
    func testCrashingResolvesToTheCrashTier() {
        let repository = ProcedureRepository()
        for query in ["crashing", "my patient is crashing", "the patient is arresting"] {
            let matches = repository.searchRescueCards(query)
            XCTAssertFalse(matches.isEmpty, "'\(query)' emptied the rescue list")
            for card in matches {
                XCTAssertEqual(card.acuity, .crash, "'\(query)' returned a non-crash card: \(card.id)")
            }
        }
    }

    /// Browsing rendered raw file order while `RescueAppIntents` told Siri and
    /// Action-button users the list was "Crash-acuity problems first".
    func testBrowsingRescueCardsPutsEveryCrashCardFirst() {
        let repository = ProcedureRepository()
        let order = repository.rescueCards.map(\.acuity.sortOrder)
        XCTAssertEqual(order, order.sorted(), "rescue cards are not acuity-ordered when browsing")
    }
}

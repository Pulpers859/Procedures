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
        ("sedation", "procedural_sedation", 3)
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
}

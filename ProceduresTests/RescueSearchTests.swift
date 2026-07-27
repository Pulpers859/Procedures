import XCTest
@testable import Procedures

/// Regression coverage for rescue-card retrieval — the crash path.
///
/// Two generations of bug here: synonym expansion once used AND-semantics so
/// shorthand returned nothing, and matching then required every typed word to
/// appear in a card, so natural phrasing ("the patient has hypotension")
/// emptied the rescue screen while "hypotension" returned five cards. These
/// lock in best-tier ranking: OR within a synonym group, keep the cards
/// satisfying the most tokens, and never fall off a cliff mid-resuscitation.
@MainActor
final class RescueSearchTests: XCTestCase {
    func testNaturalPhrasingDoesNotCollapseToZeroResults() {
        let repo = ProcedureRepository()
        for query in [
            "the patient has hypotension",
            "patient is hypotensive after intubation",
            "loss of capture",
            "my patient is crashing"
        ] {
            XCTAssertFalse(
                repo.searchRescueCards(query).isEmpty,
                "'\(query)' emptied the rescue list"
            )
        }
    }

    func testQueryNamesTheCardThatLeads() {
        let repo = ProcedureRepository()
        let leading: [(String, String)] = [
            ("hypotension", "post_intubation_hypotension"),
            ("the patient has hypotension", "post_intubation_hypotension"),
            ("laryngospasm", "laryngospasm"),
            ("last", "local_anesthetic_systemic_toxicity"),
            ("loss of capture", "failed_transvenous_capture"),
            ("cant ventilate", "failed_airway")
        ]
        for (query, expectedID) in leading {
            XCTAssertEqual(
                repo.searchRescueCards(query).first?.id, expectedID,
                "'\(query)' should lead with \(expectedID)"
            )
        }
    }

    func testPreciseMultiWordQueriesStayPrecise() {
        // Graceful degradation must not cost precision when every word matches.
        let repo = ProcedureRepository()
        XCTAssertEqual(repo.searchRescueCards("lost wire").map(\.id), ["lost_wire"])
        XCTAssertEqual(repo.searchRescueCards("capture").map(\.id), ["failed_transvenous_capture"])
        XCTAssertEqual(repo.searchRescueCards("lipid").map(\.id), ["local_anesthetic_systemic_toxicity"])
    }

    func testEditorialMetadataIsNotSearchable() {
        // Version/date strings are not clinical search text.
        let repo = ProcedureRepository()
        XCTAssertTrue(repo.searchRescueCards("0.2.0").isEmpty)
    }

    func testStopWordsAreDroppedButAnAllFillerQueryStillTokenizes() {
        XCTAssertEqual(ClinicalSynonyms.contentTokens(in: "the patient has hypotension"), ["hypotension"])
        XCTAssertFalse(ClinicalSynonyms.contentTokens(in: "the patient").isEmpty)
    }
    func testShorthandReturnsRescueCards() {
        let repo = ProcedureRepository()
        XCTAssertFalse(repo.searchRescueCards("ett").isEmpty, "ETT shorthand must return rescue cards")
        XCTAssertFalse(repo.searchRescueCards("tube").isEmpty, "tube shorthand must return rescue cards")
        XCTAssertFalse(repo.searchRescueCards("rsi").isEmpty, "RSI shorthand must return rescue cards")
    }

    func testMultiWordQueryStillNarrows() {
        let repo = ProcedureRepository()
        let results = repo.searchRescueCards("lost wire")
        XCTAssertTrue(results.contains { $0.id == "lost_wire" }, "expected the lost-wire card for a precise two-word query")
    }

    func testNonsenseQueryReturnsNothing() {
        let repo = ProcedureRepository()
        XCTAssertTrue(repo.searchRescueCards("zzzznotaclinicalterm").isEmpty)
    }

    func testEmptyQueryReturnsEveryCard() {
        let repo = ProcedureRepository()
        XCTAssertEqual(repo.searchRescueCards("   ").count, repo.rescueCards.count)
    }

    func testSynonymGroupingIsOrNotAnd() {
        // The original bug demanded every synonym be present. A token must now
        // be satisfied by itself OR any single synonym.
        let group = ClinicalSynonyms.group(for: "ett")
        XCTAssertTrue(group.contains("ett"))
        XCTAssertTrue(group.contains("intubation"))
        XCTAssertGreaterThan(group.count, 1)
    }

    func testProcedureSearchUnderstandsShorthand() {
        let repo = ProcedureRepository()
        XCTAssertTrue(repo.search("cric").contains { $0.id == "cricothyrotomy" })
        XCTAssertTrue(repo.search("lp").contains { $0.id == "lumbar_puncture" })
        XCTAssertTrue(repo.search("pacer").contains { $0.id == "transvenous_pacemaker" })
    }

    func testProcedureAndRescueShareOneSynonymSource() {
        // Both surfaces read ClinicalSynonyms, so a key defined once is visible
        // to each. Guard against the two maps drifting apart again.
        XCTAssertNotNil(ClinicalSynonyms.expansions["ett"])
        XCTAssertNotNil(ClinicalSynonyms.expansions["hypotension"])
    }
}

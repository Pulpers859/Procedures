import XCTest
@testable import Procedures

/// Decoding and content-integrity tests. These run against the JSON that ships
/// in the app bundle (the test target is hosted by the app), so they fail the
/// build if real clinical content regresses — not just synthetic fixtures.
@MainActor
final class ContentDecodingTests: XCTestCase {
    func testProceduresDecodeFromAppBundle() {
        let repo = ProcedureRepository()
        XCTAssertNil(repo.loadError, "procedures.json should decode without a fatal load error")
        XCTAssertFalse(repo.procedures.isEmpty, "expected at least one procedure to decode")
    }

    func testRescueCardsDecodeFromAppBundle() {
        let repo = ProcedureRepository()
        XCTAssertNil(repo.rescueLoadError, "rescue_cards.json should decode without a fatal load error")
        XCTAssertFalse(repo.rescueCards.isEmpty, "expected at least one rescue card to decode")
    }

    func testNoRecordsAreSilentlyDropped() {
        let repo = ProcedureRepository()
        XCTAssertNil(repo.loadWarning, "every shipped procedure must decode cleanly: \(repo.loadWarning ?? "")")
        XCTAssertNil(repo.rescueLoadWarning, "every shipped rescue card must decode cleanly: \(repo.rescueLoadWarning ?? "")")
    }

    func testShippedContentHasNoValidationBlockers() {
        let repo = ProcedureRepository()
        let blockers = repo.contentIssues.filter { $0.severity == .blocker }
        XCTAssertTrue(blockers.isEmpty, "shipped content must have no blockers: \(blockers.map(\.displayMessage))")
    }

    func testRequiredSectionsAreNonEmpty() {
        let repo = ProcedureRepository()
        for procedure in repo.procedures {
            XCTAssertFalse(procedure.sections.shiftMode.isEmpty, "\(procedure.id): empty Shift Mode")
            XCTAssertFalse(procedure.sections.equipment.isEmpty, "\(procedure.id): empty Equipment")
            XCTAssertFalse(procedure.sections.steps.isEmpty, "\(procedure.id): empty Steps")
            XCTAssertFalse(procedure.sections.references.isEmpty, "\(procedure.id): empty References")
        }
    }

    func testRescueImmediateMovesMeetMinimum() {
        let repo = ProcedureRepository()
        for card in repo.rescueCards {
            XCTAssertGreaterThanOrEqual(card.immediateMoves.count, 3, "\(card.id): needs at least 3 immediate moves")
        }
    }

    func testRescueRelatedProcedureIDsResolve() {
        let repo = ProcedureRepository()
        let ids = Set(repo.procedures.map(\.id))
        for card in repo.rescueCards {
            for related in card.relatedProcedureIDs {
                XCTAssertTrue(ids.contains(related), "rescue card \(card.id) references missing procedure \(related)")
            }
        }
    }

    func testProcedureIDsAreUnique() {
        let repo = ProcedureRepository()
        let ids = repo.procedures.map(\.id)
        XCTAssertEqual(ids.count, Set(ids).count, "procedure IDs must be unique")
    }
}

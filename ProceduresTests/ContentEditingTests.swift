import XCTest
@testable import Procedures

/// Locks the local-override layer to the one invariant that is easy to break:
/// the bundled text must be recoverable no matter which copy of a `Procedure`
/// a caller happens to hold.
///
/// `ProcedureRepository` publishes *merged* procedures, so every view hands
/// this store a value that already contains the clinician's edits. The first
/// implementation treated that value as the baseline, which made "revert to
/// bundled" restore the edit it was meant to discard.
@MainActor
final class ContentEditingTests: XCTestCase {
    private var directory: URL!
    private var suiteNames: [String] = []

    override func setUpWithError() throws {
        try super.setUpWithError()
        directory = FileManager.default.temporaryDirectory
            .appendingPathComponent("ContentEditingTests.\(UUID().uuidString)")
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
    }

    override func tearDownWithError() throws {
        try? FileManager.default.removeItem(at: directory)
        directory = nil
        for suiteName in suiteNames {
            UserDefaults().removePersistentDomain(forName: suiteName)
        }
        suiteNames = []
        try super.tearDownWithError()
    }

    // MARK: - Reverting

    func testRevertRestoresBundledTextWhenGivenTheMergedProcedure() {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])

        store.setLines(["rewritten step"], for: .steps, in: bundled)
        let merged = store.applyEdits(to: [bundled])[0]
        XCTAssertEqual(merged.sections.steps, ["rewritten step"], "the override should reach the merged copy")

        // A view only ever holds `merged`, never `bundled`.
        store.resetSection(.steps, in: merged)

        XCTAssertEqual(store.bundledLines(.steps, in: merged), bundled.sections.steps)
        XCTAssertFalse(store.isEdited(.steps, procedureID: merged.id))
        XCTAssertEqual(store.applyEdits(to: [bundled])[0].sections.steps, bundled.sections.steps)
    }

    func testRevertAllRestoresEverySectionFromTheMergedProcedure() {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])

        store.setLines(["one"], for: .steps, in: bundled)
        store.setLines(["two"], for: .complications, in: bundled)
        let merged = store.applyEdits(to: [bundled])[0]

        store.resetAllEdits(for: merged)

        XCTAssertFalse(store.hasEdits(for: bundled.id))
        let restored = store.applyEdits(to: [bundled])[0]
        XCTAssertEqual(restored.sections.steps, bundled.sections.steps)
        XCTAssertEqual(restored.sections.complications, bundled.sections.complications)
    }

    // MARK: - No-op edits

    func testRetypingTheBundledTextClearsTheOverride() {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])

        store.setLines(["rewritten step"], for: .steps, in: bundled)
        let merged = store.applyEdits(to: [bundled])[0]

        // The clinician types the original wording back in, editing the merged
        // copy. Comparing against `merged` would leave a redundant override and
        // an "EDITED" badge that could never be cleared.
        store.setLines(bundled.sections.steps, for: .steps, in: merged)

        XCTAssertFalse(store.isEdited(.steps, procedureID: bundled.id))
        XCTAssertFalse(store.hasEdits(for: bundled.id))
        XCTAssertEqual(store.editedProcedureCount, 0)
    }

    func testBlankLinesAreDiscarded() {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])

        store.setLines(["  first  ", "", "   ", "second"], for: .steps, in: bundled)

        XCTAssertEqual(store.lines(.steps, in: bundled), ["first", "second"])
    }

    // MARK: - Merge safety

    func testMergeIgnoresUnknownSectionKeys() throws {
        let bundled = makeProcedure()
        let payload = ["test": ProcedureSectionEdits(sections: ["notASection": ["x"]], editedAt: "2026-01-01")]
        let url = directory.appendingPathComponent("procedure_edits.json")
        try JSONEncoder().encode(payload).write(to: url)

        let store = makeStore()
        let merged = store.applyEdits(to: [bundled])[0]

        XCTAssertEqual(merged.sections.steps, bundled.sections.steps)
        XCTAssertEqual(merged.sections.references, bundled.sections.references)
    }

    func testPruningDropsOverridesForRemovedProcedures() {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])
        store.setLines(["kept"], for: .steps, in: bundled)

        store.pruneMissingProcedures(validProcedureIDs: ["something-else"])

        XCTAssertFalse(store.hasEdits(for: bundled.id))
    }

    func testEditsSurviveAReload() {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])
        store.setLines(["persisted"], for: .steps, in: bundled)

        let reloaded = makeStore()

        XCTAssertEqual(reloaded.applyEdits(to: [bundled])[0].sections.steps, ["persisted"])
    }

    // MARK: - Export

    func testExportCarriesTheSchemaTheApplyScriptExpects() throws {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])
        store.setLines(["exported"], for: .steps, in: bundled)

        let object = try XCTUnwrap(
            JSONSerialization.jsonObject(with: try store.exportData()) as? [String: Any]
        )

        // scripts/apply_local_edits.py refuses any other schema string.
        XCTAssertEqual(object["schema"] as? String, "procedures.local-edits.v1")
        let edits = try XCTUnwrap(object["edits"] as? [String: Any])
        let entry = try XCTUnwrap(edits["test"] as? [String: Any])
        let sections = try XCTUnwrap(entry["sections"] as? [String: Any])
        XCTAssertEqual(sections["steps"] as? [String], ["exported"])
    }

    // MARK: - Reviews vs. your own edits

    func testEditingContentYouReviewedDoesNotFlagYourOwnReview() throws {
        let bundled = makeProcedure()
        let store = makeStore()
        _ = store.applyEdits(to: [bundled])

        let userData = makeUserDataStore()
        userData.markReviewed(bundled)
        XCTAssertEqual(userData.reviewContentState(for: bundled), .unchanged)

        store.setLines(["a materially different step"], for: .steps, in: bundled)
        let edited = store.applyEdits(to: [bundled])[0]

        // Before re-baselining this reads as .materialChanged — the clinician
        // being told to re-review a correction they just wrote themselves.
        XCTAssertEqual(userData.reviewContentState(for: edited), .materialChanged)

        userData.rebaselineReviewAfterLocalEdit(for: edited)

        XCTAssertEqual(userData.reviewContentState(for: edited), .unchanged)
        XCTAssertEqual(userData.localReviewRecord(for: edited)?.disposition, .reviewed)
    }

    func testRebaselineDoesNotCreateAReviewWhereThereWasNone() {
        let bundled = makeProcedure()
        let userData = makeUserDataStore()

        userData.rebaselineReviewAfterLocalEdit(for: bundled)

        XCTAssertNil(userData.localReviewRecord(for: bundled))
    }

    func testUpstreamChangeStillFlagsAReviewedProcedure() {
        let bundled = makeProcedure()
        let userData = makeUserDataStore()
        userData.markReviewed(bundled)

        // Content that moved underneath the reviewer, with no local edit.
        var shipped = bundled
        shipped.sections.steps = ["a new step from the repo"]

        XCTAssertEqual(userData.reviewContentState(for: shipped), .materialChanged)
    }

    // MARK: - Swift/Python fingerprint mirror

    /// `scripts/apply_local_reviews.py` recomputes the material fingerprint to
    /// refuse promoting a sign-off onto content that has since changed. That
    /// check is only worth anything if the Python mirror agrees with Swift
    /// byte for byte, and nothing else in either suite would notice them
    /// drifting apart. These digests are produced by the Python implementation.
    func testMaterialFingerprintMatchesThePythonMirror() {
        XCTAssertEqual(
            makeProcedure().materialFingerprint,
            "4206af11db9e97d0075e96dc97f6553010e4b19e2f21131d500d9d83fb86a18f"
        )
    }

    func testDosingFingerprintMatchesThePythonMirror() {
        let procedure = makeProcedure(dosing: ProcedureDosing(
            agents: [
                ProcedureDosing.Agent(
                    agent: "Lidocaine 1%",
                    concentrationNote: "1% = 10 mg/mL",
                    maxDoseMgPerKg: 4.5,
                    absoluteMaxMg: 300
                ),
                ProcedureDosing.Agent(
                    agent: "Bupivacaine",
                    concentrationNote: "0.25% = 2.5 mg/mL",
                    maxDoseMgPerKg: 2.0,
                    absoluteMaxMg: nil
                ),
            ],
            workedExample: "unused by the fingerprint",
            cumulativeWarning: "Count every source.",
            monitoring: ["unused by the fingerprint"],
            rescueCardID: nil
        ))

        XCTAssertEqual(
            procedure.materialFingerprint,
            "6dd99615dd8f6ba8079c2c1569e9a3e98b57617672e14d25853cdde18cc0a5aa"
        )
    }

    // MARK: - Fixtures

    private func makeUserDataStore() -> UserDataStore {
        let suiteName = "ContentEditingTests.\(UUID().uuidString)"
        let defaults = UserDefaults(suiteName: suiteName)!
        defaults.removePersistentDomain(forName: suiteName)
        suiteNames.append(suiteName)
        return UserDataStore(defaults: defaults)
    }

    private func makeStore() -> ProcedureEditStore {
        ProcedureEditStore(directory: directory)
    }

    private func makeProcedure(id: String = "test", dosing: ProcedureDosing? = nil) -> Procedure {
        Procedure(
            id: id,
            title: "Test Procedure",
            category: .other,
            difficulty: .basic,
            reviewTime: "1 min",
            setting: [.ed],
            lastReviewed: "2026-01-01",
            version: "1.0",
            tags: ["test"],
            visualAssets: nil,
            dosing: dosing,
            reviewerStatus: .internallyReviewed,
            contentSource: .clinicianReviewed,
            sections: ProcedureSections(
                shiftMode: ["a", "b", "c", "d", "e", "f"],
                indications: ["a"],
                contraindications: ["a"],
                anatomy: ["a"],
                equipment: ["a", "b", "c", "d", "e"],
                positioning: ["a"],
                steps: ["a", "b", "c", "d", "e"],
                ultrasound: [],
                confirmation: ["a"],
                troubleshooting: ["a", "b", "c"],
                complications: ["a", "b", "c", "d"],
                aftercare: ["a"],
                documentation: ["a", "b", "c", "d"],
                seniorPearls: ["a", "b"],
                references: ["Smith et al. 2024"]
            )
        )
    }
}

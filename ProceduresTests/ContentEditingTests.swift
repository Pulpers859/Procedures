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

        userData.rebaselineReviewAfterLocalEdit(
            for: edited,
            previousFingerprint: bundled.materialFingerprint
        )

        XCTAssertEqual(userData.reviewContentState(for: edited), .unchanged)
        XCTAssertEqual(userData.localReviewRecord(for: edited)?.disposition, .reviewed)
    }

    func testRebaselineDoesNotCreateAReviewWhereThereWasNone() {
        let bundled = makeProcedure()
        let userData = makeUserDataStore()

        userData.rebaselineReviewAfterLocalEdit(
            for: bundled,
            previousFingerprint: bundled.materialFingerprint
        )

        XCTAssertNil(userData.localReviewRecord(for: bundled))
    }

    /// The bug this guard exists for.
    ///
    /// `SectionEditorView.onDisappear` saves whether or not anything was
    /// typed, and the rebaseline adopted the current fingerprint without
    /// asking why it differed. So a procedure whose bundled text had changed
    /// since sign-off — correctly reading "Review out of date" — was returned
    /// to a plain "Reviewed" by opening any section, reading nothing, and
    /// tapping Back. The upstream change stayed unread and the notice was gone.
    func testAnUnrelatedEditDoesNotClearAnExistingOutOfDateNotice() {
        let bundled = makeProcedure()
        let userData = makeUserDataStore()
        userData.markReviewed(bundled)

        // The repo ships a rewritten step the reader has not seen.
        var shipped = bundled
        shipped.sections.steps = ["a new step from the repo"]
        XCTAssertEqual(userData.reviewContentState(for: shipped), .materialChanged)

        // The reader now edits something else entirely, or simply visits a
        // section editor and backs out. Either way the pre-edit fingerprint is
        // the shipped one, which is not what they signed off.
        userData.rebaselineReviewAfterLocalEdit(
            for: shipped,
            previousFingerprint: shipped.materialFingerprint
        )

        XCTAssertEqual(
            userData.reviewContentState(for: shipped), .materialChanged,
            "an unrelated edit must not retire an unread upstream change"
        )
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
            "4c52bd50d9863784bbbca02fc13ca52d47e56218894f5bae6bab8339cb431ca9"
        )
    }

    func testDosingFingerprintMatchesThePythonMirror() {
        let procedure = makeProcedure(dosing: ProcedureDosing(
            agents: [
                ProcedureDosing.Agent(
                    agent: "Lidocaine",
                    withEpinephrine: false,
                    maxDoseMgPerKg: 4.5,
                    absoluteMaxMg: 300,
                    concentrationsPercent: [1.0, 2.0]
                ),
                ProcedureDosing.Agent(
                    agent: "Lidocaine",
                    withEpinephrine: true,
                    maxDoseMgPerKg: 7.0,
                    absoluteMaxMg: nil,
                    concentrationsPercent: [1.0]
                ),
            ],
            cumulativeWarning: "Count every source.",
            monitoring: ["unused by the fingerprint"],
            rescueCardID: nil
        ))

        XCTAssertEqual(
            procedure.materialFingerprint,
            "380113dd41c18cf859ef7995625b78a25fa98bcf912d5a60e2ae9fb85034b6f2"
        )
    }

    /// Rescue cards and kits promote through the same refusal check, and until
    /// now neither had a locked digest on either side. The field *order* is the
    /// fragile part: `immediateMoves + trigger + avoid + reassess` reads
    /// naturally in neither language, so the fixtures name their own field to
    /// make a reordered mirror fail loudly instead of quietly refusing every
    /// sign-off the clinician exports.
    func testRescueCardFingerprintMatchesThePythonMirror() {
        XCTAssertEqual(
            makeRescueCard().materialFingerprint,
            "2cd50e72af4bc51bff2c24b3fbda37fccfafc46249e5d3c7b75fc807d1d39321"
        )
    }

    func testKitFingerprintMatchesThePythonMirror() {
        XCTAssertEqual(
            makeKit().materialFingerprint,
            "ebeceacf2b5a456d02f5481f103887fa3f5e63ea8305eeaa6d2c1ae0b8f50b67"
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

    /// Field-naming strings, not "a"/"b"/"c": the point of this fixture is to
    /// catch a mirror that concatenates the same fields in a different order.
    private func makeRescueCard() -> ComplicationRescueCard {
        ComplicationRescueCard(
            id: "test-card",
            title: "Test Card",
            acuity: .crash,
            relatedProcedureIDs: ["test"],
            trigger: ["tr1"],
            immediateMoves: ["im1", "im2"],
            reassess: ["re1"],
            avoid: ["av1"],
            tags: ["excluded from the fingerprint"],
            lastReviewed: "2026-01-01",
            version: "1.0",
            references: ["excluded from the fingerprint"],
            reviewerStatus: .internallyReviewed,
            contentSource: .clinicianReviewed
        )
    }

    private func makeKit() -> Kit {
        Kit(
            id: "test-kit",
            title: "Test Kit",
            subtitle: "excluded from the fingerprint",
            category: .other,
            relatedProcedureIDs: ["test"],
            tags: ["excluded from the fingerprint"],
            lastReviewed: "2026-01-01",
            version: "1.0",
            reviewerStatus: .internallyReviewed,
            contentSource: .clinicianReviewed,
            inKit: ["ik1", "ik2"],
            outsideKit: ["ok1"],
            commonlyForgotten: ["cf1"],
            patientSetup: ["ps1"],
            sterileSetup: ["ss1"],
            backupEquipment: ["excluded from the fingerprint"],
            references: ["excluded from the fingerprint"]
        )
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

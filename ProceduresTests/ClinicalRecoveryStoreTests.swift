import XCTest
@testable import Procedures

@MainActor
final class ClinicalRecoveryStoreTests: XCTestCase {
    private var directory: URL!
    private var defaults: UserDefaults!
    private var suiteName: String!

    override func setUpWithError() throws {
        directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        suiteName = "ClinicalRecoveryStoreTests.\(UUID().uuidString)"
        defaults = UserDefaults(suiteName: suiteName)!
    }

    override func tearDownWithError() throws {
        if let suiteName { UserDefaults().removePersistentDomain(forName: suiteName) }
        if let directory { try? FileManager.default.removeItem(at: directory) }
    }

    private func makeStores() -> (UserDataStore, ProcedureEditStore, ClinicalRecoveryStore) {
        (
            UserDataStore(defaults: defaults),
            ProcedureEditStore(directory: directory),
            ClinicalRecoveryStore(directory: directory.appendingPathComponent("backups"))
        )
    }

    private func procedure() -> Procedure {
        Procedure(
            id: "recovery_test",
            title: "Recovery Test",
            category: .other,
            difficulty: .basic,
            reviewTime: "60 sec",
            setting: [.ed],
            lastReviewed: "2026-01-01",
            version: "1.0.0",
            tags: [],
            visualAssets: nil,
            dosing: nil,
            medicationDosing: nil,
            reviewerStatus: .draft,
            contentSource: .aiDraft,
            sections: ProcedureSections(
                shiftMode: ["Prepare"], indications: [], contraindications: [], anatomy: [], equipment: [],
                positioning: [], steps: ["Original step"], ultrasound: [], confirmation: [], troubleshooting: [],
                complications: [], aftercare: [], documentation: [], seniorPearls: [], references: []
            )
        )
    }

    func testSnapshotRoundTripRestoresMissingLocalEdit() throws {
        let (userData, editStore, recovery) = makeStores()
        let procedure = procedure()
        _ = editStore.applyEdits(to: [procedure])
        editStore.setLines(["Edited step"], for: .steps, in: procedure)
        recovery.snapshotNow(userData: userData, editStore: editStore)

        let snapshot = try XCTUnwrap(recovery.snapshots.first)
        let preview = try recovery.previewImport(from: snapshot.url, editStore: ProcedureEditStore(directory: directory.appendingPathComponent("fresh")), procedures: [procedure])
        XCTAssertTrue(preview.canRestoreSafely)
        XCTAssertEqual(preview.package.edits[procedure.id]?.sections[EditableSection.steps.rawValue], ["Edited step"])
    }

    func testRestoreDoesNotOverwriteCurrentConflictByDefault() throws {
        let (userData, editStore, recovery) = makeStores()
        let procedure = procedure()
        _ = editStore.applyEdits(to: [procedure])
        editStore.setLines(["Backup step"], for: .steps, in: procedure)
        let url = try XCTUnwrap(recovery.writePortableExport(userData: userData, editStore: editStore))

        editStore.setLines(["Current step"], for: .steps, in: procedure)
        let preview = try recovery.previewImport(from: url, editStore: editStore, procedures: [procedure])
        XCTAssertEqual(preview.conflicts, [procedure.id])
        XCTAssertFalse(preview.canRestoreSafely)
    }

    func testSnapshotsRotateToThreeGenerations() {
        let (userData, editStore, recovery) = makeStores()
        let procedure = procedure()
        _ = editStore.applyEdits(to: [procedure])
        for index in 0..<4 {
            editStore.setLines(["Step \(index)"], for: .steps, in: procedure)
            recovery.snapshotNow(userData: userData, editStore: editStore)
        }
        XCTAssertEqual(recovery.snapshots.count, 3)
    }
}

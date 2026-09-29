import UIKit
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

    func testPortableExportCarriesImportedImagesAndPreviewFlagsDifferences() throws {
        let (userData, editStore, recovery) = makeStores()
        let images = directory.appendingPathComponent("backups").appendingPathComponent("ImportedVisuals")
        let jpeg = try XCTUnwrap(UIGraphicsImageRenderer(size: CGSize(width: 4, height: 4)).image { context in
            UIColor.red.setFill()
            context.fill(CGRect(x: 0, y: 0, width: 4, height: 4))
        }.jpegData(compressionQuality: 0.9))
        try ImportedVisualStore.writeData(jpeg, for: "pigtail_us_effusion", in: images)

        let url = try XCTUnwrap(recovery.writePortableExport(userData: userData, editStore: editStore))
        var preview = try recovery.previewImport(from: url, editStore: editStore, procedures: [procedure()])
        XCTAssertEqual(preview.package.importedVisuals?["pigtail_us_effusion"], jpeg)
        XCTAssertEqual(preview.imageCount, 1)
        XCTAssertTrue(preview.imageConflicts.isEmpty, "the same bytes on device are not a conflict")

        let other = try XCTUnwrap(UIGraphicsImageRenderer(size: CGSize(width: 4, height: 4)).image { context in
            UIColor.blue.setFill()
            context.fill(CGRect(x: 0, y: 0, width: 4, height: 4))
        }.jpegData(compressionQuality: 0.9))
        try ImportedVisualStore.writeData(other, for: "pigtail_us_effusion", in: images)
        preview = try recovery.previewImport(from: url, editStore: editStore, procedures: [procedure()])
        XCTAssertEqual(preview.imageConflicts, ["pigtail_us_effusion"])
        XCTAssertFalse(preview.canRestoreSafely)
        XCTAssertTrue(preview.hasReplaceableConflicts)
    }

    func testAutomaticSnapshotsLeaveImagesOut() throws {
        let (userData, editStore, recovery) = makeStores()
        let images = directory.appendingPathComponent("backups").appendingPathComponent("ImportedVisuals")
        let jpeg = try XCTUnwrap(UIGraphicsImageRenderer(size: CGSize(width: 2, height: 2)).image { _ in }.jpegData(compressionQuality: 0.9))
        try ImportedVisualStore.writeData(jpeg, for: "ij_probe_orientation", in: images)
        let procedure = procedure()
        _ = editStore.applyEdits(to: [procedure])
        editStore.setLines(["Edited step"], for: .steps, in: procedure)
        recovery.snapshotNow(userData: userData, editStore: editStore)
        XCTAssertNil(try XCTUnwrap(recovery.snapshots.first).package.importedVisuals)
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

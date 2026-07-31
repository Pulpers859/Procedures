import Foundation

/// Portable, clinician-owned state. It intentionally excludes bundled JSON:
/// GitHub is the source of truth for shipped content, while this package saves
/// only what a person created on one device.
struct ClinicalRecoveryUserData: Codable, Hashable {
    var favoriteIDs: [String]
    var recentIDs: [String]
    var notes: [String: String]
    var checkedEquipment: [String: [String]]
    var kitCheckedItems: [String: [String]]
    var locallyReviewedContent: [String: LocalReviewRecord]
}

struct ClinicalRecoveryPackage: Codable, Hashable {
    static let schema = "procedures.clinician-recovery.v1"
    static let formatVersion = 1

    let schema: String
    let formatVersion: Int
    let exportedAt: String
    let appVersion: String
    let edits: [String: ProcedureSectionEdits]
    let userData: ClinicalRecoveryUserData
}

struct ClinicalRecoverySnapshot: Identifiable, Hashable {
    let url: URL
    let package: ClinicalRecoveryPackage

    var id: URL { url }
    var date: String { package.exportedAt }
    var procedureEditCount: Int { package.edits.count }
}

struct ClinicalRecoveryPreview: Identifiable {
    let package: ClinicalRecoveryPackage
    let conflicts: [String]
    let staleProcedureIDs: [String]
    let unknownProcedureIDs: [String]

    var id: String { package.exportedAt + package.appVersion }
    var canRestoreSafely: Bool { conflicts.isEmpty && staleProcedureIDs.isEmpty && unknownProcedureIDs.isEmpty }
}

enum ClinicalRecoveryError: LocalizedError {
    case unsupportedSchema
    case unsupportedVersion(Int)
    case invalidPackage

    var errorDescription: String? {
        switch self {
        case .unsupportedSchema: return "This file is not a Procedures recovery package."
        case .unsupportedVersion(let version): return "This recovery package uses unsupported format version \(version)."
        case .invalidPackage: return "The recovery package could not be read."
        }
    }
}

@MainActor
final class ClinicalRecoveryStore: ObservableObject {
    @Published private(set) var snapshots: [ClinicalRecoverySnapshot] = []
    @Published private(set) var lastError: String?
    @Published private(set) var lastAutomaticBackupDate: String?

    private let fileManager: FileManager
    private let directory: URL
    private var pendingSnapshotTask: Task<Void, Never>?
    private var lastSignature: Data?
    private let now: () -> Date

    init(directory: URL? = nil, fileManager: FileManager = .default, now: @escaping () -> Date = Date.init) {
        self.fileManager = fileManager
        self.now = now
        let base = directory ?? fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? fileManager.temporaryDirectory
        self.directory = base.appendingPathComponent("ClinicalRecovery", isDirectory: true)
        refreshSnapshots()
    }

    deinit { pendingSnapshotTask?.cancel() }

    func scheduleAutomaticSnapshot(userData: UserDataStore, editStore: ProcedureEditStore) {
        guard !userData.hasUnreadableData, !editStore.hasUnreadableEdits else { return }
        pendingSnapshotTask?.cancel()
        pendingSnapshotTask = Task { [weak self, weak userData, weak editStore] in
            try? await Task.sleep(nanoseconds: 1_000_000_000)
            guard !Task.isCancelled, let self, let userData, let editStore else { return }
            self.snapshotNow(userData: userData, editStore: editStore)
        }
    }

    func snapshotNow(userData: UserDataStore, editStore: ProcedureEditStore) {
        guard !userData.hasUnreadableData, !editStore.hasUnreadableEdits else { return }
        do {
            let package = makePackage(userData: userData, editStore: editStore)
            let signature = try canonicalContentsData(for: package)
            guard signature != lastSignature else { return }
            try write(package, kind: "auto")
            lastSignature = signature
            lastAutomaticBackupDate = package.exportedAt
        } catch {
            lastError = "Automatic backup failed: \(error.localizedDescription)"
        }
    }

    /// Used before a destructive local-data action. Unlike routine autosave it
    /// always writes a fresh generation, but refuses to bless a partially
    /// unreadable primary store as a recovery point.
    func makeSafetySnapshot(userData: UserDataStore, editStore: ProcedureEditStore) -> Bool {
        guard !userData.hasUnreadableData, !editStore.hasUnreadableEdits else {
            lastError = "Cannot create a safety backup while some saved data is unreadable. Restore a recovery package first."
            return false
        }
        do {
            let package = makePackage(userData: userData, editStore: editStore)
            try write(package, kind: "safety")
            lastSignature = try canonicalContentsData(for: package)
            return true
        } catch {
            lastError = "Safety backup failed: \(error.localizedDescription)"
            return false
        }
    }

    func writePortableExport(userData: UserDataStore, editStore: ProcedureEditStore) -> URL? {
        do {
            let package = makePackage(userData: userData, editStore: editStore)
            let url = fileManager.temporaryDirectory.appendingPathComponent("procedures-clinician-recovery-\(fileDate()).json")
            try encodedData(for: package).write(to: url, options: .atomic)
            return url
        } catch {
            lastError = "Could not prepare recovery package: \(error.localizedDescription)"
            return nil
        }
    }

    func previewImport(
        from url: URL,
        editStore: ProcedureEditStore,
        procedures: [Procedure]
    ) throws -> ClinicalRecoveryPreview {
        let accessGranted = url.startAccessingSecurityScopedResource()
        defer { if accessGranted { url.stopAccessingSecurityScopedResource() } }
        let package = try decodePackage(from: Data(contentsOf: url))
        let current = editStore.editsByProcedureID
        let validIDs = Set(procedures.map(\.id))
        let unknown = package.edits.keys.filter { !validIDs.contains($0) }.sorted()
        let conflicts = package.edits.keys.filter { current[$0] != nil && current[$0] != package.edits[$0] }.sorted()
        let stale = package.edits.compactMap { procedureID, edit -> String? in
            guard let baseline = edit.baseMaterialFingerprint,
                  let currentFingerprint = editStore.bundledMaterialFingerprint(for: procedureID, in: procedures)
            else { return procedureID }
            return baseline == currentFingerprint ? nil : procedureID
        }.sorted()
        return ClinicalRecoveryPreview(package: package, conflicts: conflicts, staleProcedureIDs: stale, unknownProcedureIDs: unknown)
    }

    /// Safe restore fills only missing state. Replace mode is explicit in the
    /// UI and is used only after the clinician has seen every conflict.
    func restore(
        _ preview: ClinicalRecoveryPreview,
        replacingConflicts: Bool,
        userData: UserDataStore,
        editStore: ProcedureEditStore,
        repository: ProcedureRepository
    ) {
        snapshotNow(userData: userData, editStore: editStore)
        let allowedEdits = preview.package.edits.compactMapValues { edit -> ProcedureSectionEdits? in
            let sections = edit.sections.filter { EditableSection(rawValue: $0.key) != nil }
            guard !sections.isEmpty else { return nil }
            var sanitized = edit
            sanitized.sections = sections
            return sanitized
        }.filter { !preview.unknownProcedureIDs.contains($0.key) }
        if replacingConflicts {
            editStore.restoreRecoveryEdits(allowedEdits, replacingConflicts: true)
        } else {
            let safeEdits = allowedEdits.filter { !preview.conflicts.contains($0.key) && !preview.staleProcedureIDs.contains($0.key) }
            editStore.restoreRecoveryEdits(safeEdits, replacingConflicts: false)
        }
        userData.restoreRecoverySnapshot(preview.package.userData, replacingConflicts: replacingConflicts)
        userData.markRecoveryRestored()
        editStore.markRecoveryRestored()
        repository.reapplyEdits()
        snapshotNow(userData: userData, editStore: editStore)
    }

    func refreshSnapshots() {
        do {
            try fileManager.createDirectory(at: directory, withIntermediateDirectories: true)
            let urls = try fileManager.contentsOfDirectory(at: directory, includingPropertiesForKeys: nil)
                .filter { $0.pathExtension == "json" }
            snapshots = urls.compactMap { url in
                guard let data = try? Data(contentsOf: url), let package = try? decodePackage(from: data) else { return nil }
                return ClinicalRecoverySnapshot(url: url, package: package)
            }.sorted { $0.package.exportedAt > $1.package.exportedAt }
            lastAutomaticBackupDate = snapshots.first?.package.exportedAt
            lastSignature = snapshots.first.flatMap { try? canonicalContentsData(for: $0.package) }
        } catch {
            lastError = "Could not read recovery snapshots: \(error.localizedDescription)"
        }
    }

    private func makePackage(userData: UserDataStore, editStore: ProcedureEditStore) -> ClinicalRecoveryPackage {
        ClinicalRecoveryPackage(
            schema: ClinicalRecoveryPackage.schema,
            formatVersion: ClinicalRecoveryPackage.formatVersion,
            exportedAt: displayDate(),
            appVersion: AppConstants.appVersionDescription,
            edits: editStore.editsByProcedureID,
            userData: userData.recoverySnapshot()
        )
    }

    private func write(_ package: ClinicalRecoveryPackage, kind: String) throws {
        try fileManager.createDirectory(at: directory, withIntermediateDirectories: true)
        let url = directory.appendingPathComponent("procedures-recovery-\(fileDate())-\(UUID().uuidString)-\(kind).json")
        try encodedData(for: package).write(to: url, options: [.atomic, .completeFileProtection])
        let old = snapshots.sorted { $0.package.exportedAt > $1.package.exportedAt }.dropFirst(2)
        for snapshot in old { try? fileManager.removeItem(at: snapshot.url) }
        refreshSnapshots()
    }

    private func decodePackage(from data: Data) throws -> ClinicalRecoveryPackage {
        guard let package = try? JSONDecoder().decode(ClinicalRecoveryPackage.self, from: data) else {
            throw ClinicalRecoveryError.invalidPackage
        }
        guard package.schema == ClinicalRecoveryPackage.schema else { throw ClinicalRecoveryError.unsupportedSchema }
        guard package.formatVersion == ClinicalRecoveryPackage.formatVersion else {
            throw ClinicalRecoveryError.unsupportedVersion(package.formatVersion)
        }
        return package
    }

    private func encodedData(for package: ClinicalRecoveryPackage) throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return try encoder.encode(package)
    }

    private func canonicalContentsData(for package: ClinicalRecoveryPackage) throws -> Data {
        let copy = ClinicalRecoveryPackage(
            schema: package.schema,
            formatVersion: package.formatVersion,
            exportedAt: "",
            appVersion: package.appVersion,
            edits: package.edits,
            userData: package.userData
        )
        return try encodedData(for: copy)
    }

    private func displayDate() -> String {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        return formatter.string(from: now())
    }

    private func fileDate() -> String {
        displayDate().replacingOccurrences(of: ":", with: "-")
    }
}

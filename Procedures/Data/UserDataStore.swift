import Foundation

private enum UserDataStoreKey {
    static let favorites = "Procedures.favoriteIDs"
    static let recents = "Procedures.recentIDs"
    static let notes = "Procedures.notes"
    static let checkedEquipment = "Procedures.checkedEquipment"
    static let kitCheckedItems = "Procedures.kitCheckedItems"
    static let locallyReviewedContent = "Procedures.locallyReviewedContent"

    static let legacyFavorites = "ProcedureSTAT.favoriteIDs"
    static let legacyRecents = "ProcedureSTAT.recentIDs"
    static let legacyNotes = "ProcedureSTAT.notes"
    static let legacyCheckedEquipment = "ProcedureSTAT.checkedEquipment"
}

enum LocalReviewDisposition: String, Codable, CaseIterable, Identifiable {
    case reviewed = "Reviewed"
    case needsEdits = "Needs Edits"
    case deferred = "Deferred"

    var id: String { rawValue }

    var systemImage: String {
        switch self {
        case .reviewed: return "checkmark.seal.fill"
        case .needsEdits: return "square.and.pencil"
        case .deferred: return "clock"
        }
    }
}

/// How a stored review relates to the content bundled today.
///
/// A review is the clinician's own work and is never revoked: it keeps its
/// disposition, stays in the reviewed list, and keeps counting toward
/// progress no matter what ships later. The only thing tracked here is whether
/// the *clinically material* text — steps, doses, contraindications,
/// complications — moved since they last looked, so the app can mention it
/// once instead of quietly implying they approved words they never saw.
/// Editorial churn (tags, references, formatting, version bumps) is invisible
/// by design; a warning that fires on every update is a warning nobody reads.
enum ReviewContentState: Hashable {
    /// The material content is exactly what was reviewed.
    case unchanged
    /// Steps, doses, contraindications, or complications changed since review.
    case materialChanged
    /// Written before fingerprints were recorded, so no comparison is possible.
    /// Not a problem to fix — just an unknown, and reported as nothing at all.
    case unknownBaseline
}

struct LocalReviewRecord: Codable, Hashable {
    let disposition: LocalReviewDisposition
    let date: String
    /// Bundled content version at review time. Informational only — shown to
    /// give the date context. It deliberately does NOT drive re-review, because
    /// a version bump for a typo must not disturb a sign-off.
    var contentVersion: String?
    /// Fingerprint of the clinically material content at review time. This is
    /// what re-review keys on. Optional so pre-fingerprint records still decode.
    var materialFingerprint: String?

    /// Compares the material baseline against the content bundled today.
    func contentState(currentFingerprint: String) -> ReviewContentState {
        guard let materialFingerprint, !materialFingerprint.isEmpty else { return .unknownBaseline }
        return materialFingerprint == currentFingerprint ? .unchanged : .materialChanged
    }
}

@MainActor
final class UserDataStore: ObservableObject {
    private let defaults: UserDefaults
    @Published private(set) var favoriteIDs: Set<String> = []
    @Published private(set) var recentIDs: [String] = []
    @Published private(set) var notes: [String: String] = [:]
    @Published private(set) var checkedEquipment: [String: Set<String>] = [:]
    @Published private(set) var kitCheckedItems: [String: Set<String>] = [:]
    @Published private(set) var locallyReviewedContent: [String: LocalReviewRecord] = [:]
    @Published private(set) var activeEquipmentSessionIDs: Set<String> = []
    @Published private(set) var activeKitSessionIDs: Set<String> = []

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
        load()
    }

    func isFavorite(_ procedure: Procedure) -> Bool {
        favoriteIDs.contains(procedure.id)
    }

    func toggleFavorite(_ procedure: Procedure) {
        if favoriteIDs.contains(procedure.id) {
            favoriteIDs.remove(procedure.id)
        } else {
            favoriteIDs.insert(procedure.id)
        }
        saveFavorites()
    }

    func markRecentlyViewed(_ procedure: Procedure) {
        recentIDs.removeAll { $0 == procedure.id }
        recentIDs.insert(procedure.id, at: 0)
        if recentIDs.count > AppConstants.maxRecents {
            recentIDs = Array(recentIDs.prefix(AppConstants.maxRecents))
        }
        saveRecents()
    }

    func note(for procedure: Procedure) -> String {
        notes[procedure.id, default: ""]
    }

    func setNote(_ note: String, for procedure: Procedure) {
        let trimmed = note.trimmingCharacters(in: .whitespacesAndNewlines)
        if trimmed.isEmpty {
            notes.removeValue(forKey: procedure.id)
        } else {
            notes[procedure.id] = note
        }
        saveNotes()
    }

    func isEquipmentChecked(_ item: String, for procedure: Procedure) -> Bool {
        checkedEquipment[procedure.id, default: []].contains(item)
    }

    func toggleEquipment(_ item: String, for procedure: Procedure) {
        activeEquipmentSessionIDs.insert(procedure.id)
        var procedureSet = checkedEquipment[procedure.id, default: []]
        if procedureSet.contains(item) {
            procedureSet.remove(item)
        } else {
            procedureSet.insert(item)
        }
        checkedEquipment[procedure.id] = procedureSet
        saveCheckedEquipment()
    }

    func resetEquipment(for procedure: Procedure) {
        activeEquipmentSessionIDs.insert(procedure.id)
        checkedEquipment[procedure.id] = []
        saveCheckedEquipment()
    }

    func requiresEquipmentSessionDecision(for procedure: Procedure) -> Bool {
        !checkedEquipment[procedure.id, default: []].isEmpty
            && !activeEquipmentSessionIDs.contains(procedure.id)
    }

    func resumeEquipmentSession(for procedure: Procedure) {
        activeEquipmentSessionIDs.insert(procedure.id)
    }

    // MARK: - Kit checklist

    func isKitItemChecked(_ item: String, forKitID kitID: String) -> Bool {
        kitCheckedItems[kitID, default: []].contains(item)
    }

    func toggleKitItem(_ item: String, forKitID kitID: String) {
        activeKitSessionIDs.insert(kitID)
        var kitSet = kitCheckedItems[kitID, default: []]
        if kitSet.contains(item) {
            kitSet.remove(item)
        } else {
            kitSet.insert(item)
        }
        kitCheckedItems[kitID] = kitSet
        saveKitCheckedItems()
    }

    func resetKit(withID kitID: String) {
        activeKitSessionIDs.insert(kitID)
        kitCheckedItems[kitID] = []
        saveKitCheckedItems()
    }

    func requiresKitSessionDecision(forKitID kitID: String) -> Bool {
        !kitCheckedItems[kitID, default: []].isEmpty
            && !activeKitSessionIDs.contains(kitID)
    }

    func resumeKitSession(withID kitID: String) {
        activeKitSessionIDs.insert(kitID)
    }

    // MARK: - Local review status

    func localReviewRecord(for procedure: Procedure) -> LocalReviewRecord? {
        locallyReviewedContent[reviewKey(kind: "procedure", id: procedure.id)]
    }

    func localReviewRecord(for card: ComplicationRescueCard) -> LocalReviewRecord? {
        locallyReviewedContent[reviewKey(kind: "rescue", id: card.id)]
    }

    func localReviewRecord(for kit: Kit) -> LocalReviewRecord? {
        locallyReviewedContent[reviewKey(kind: "kit", id: kit.id)]
    }

    func localReviewDate(for procedure: Procedure) -> String? {
        localReviewRecord(for: procedure)?.date
    }

    func localReviewDate(for card: ComplicationRescueCard) -> String? {
        localReviewRecord(for: card)?.date
    }

    func localReviewDate(for kit: Kit) -> String? {
        localReviewRecord(for: kit)?.date
    }

    func markReviewed(_ procedure: Procedure) {
        setReviewDisposition(.reviewed, for: procedure)
    }

    func markReviewed(_ card: ComplicationRescueCard) {
        setReviewDisposition(.reviewed, for: card)
    }

    func markReviewed(_ kit: Kit) {
        setReviewDisposition(.reviewed, for: kit)
    }

    func setReviewDisposition(_ disposition: LocalReviewDisposition, for procedure: Procedure) {
        setLocalReviewRecord(
            forKey: reviewKey(kind: "procedure", id: procedure.id),
            disposition: disposition,
            contentVersion: procedure.version,
            materialFingerprint: procedure.materialFingerprint
        )
    }

    func setReviewDisposition(_ disposition: LocalReviewDisposition, for card: ComplicationRescueCard) {
        setLocalReviewRecord(
            forKey: reviewKey(kind: "rescue", id: card.id),
            disposition: disposition,
            contentVersion: card.version,
            materialFingerprint: card.materialFingerprint
        )
    }

    func setReviewDisposition(_ disposition: LocalReviewDisposition, for kit: Kit) {
        setLocalReviewRecord(
            forKey: reviewKey(kind: "kit", id: kit.id),
            disposition: disposition,
            contentVersion: kit.version,
            materialFingerprint: kit.materialFingerprint
        )
    }

    /// Re-baselines an existing review against content the reviewer just edited
    /// themselves.
    ///
    /// Without this, correcting a step in a procedure you had already signed off
    /// flagged you about your own change — the same cry-wolf behaviour that made
    /// version-bound sign-offs useless. The material-change notice is for
    /// content that moved underneath you, not for work you did. The disposition
    /// and the original review date are both preserved: this re-points the
    /// baseline, it does not re-date the review.
    func rebaselineReviewAfterLocalEdit(for procedure: Procedure) {
        let key = reviewKey(kind: "procedure", id: procedure.id)
        guard var record = locallyReviewedContent[key] else { return }
        guard record.materialFingerprint != procedure.materialFingerprint else { return }
        record.materialFingerprint = procedure.materialFingerprint
        record.contentVersion = procedure.version
        locallyReviewedContent[key] = record
        saveLocallyReviewedContent()
    }

    // MARK: - Review content state

    /// Whether the clinically material content changed since it was reviewed.
    /// A review is never revoked by this: it is informational so the clinician
    /// can glance and re-confirm rather than redo work they already did.
    func reviewContentState(for procedure: Procedure) -> ReviewContentState? {
        localReviewRecord(for: procedure)?.contentState(currentFingerprint: procedure.materialFingerprint)
    }

    func reviewContentState(for card: ComplicationRescueCard) -> ReviewContentState? {
        localReviewRecord(for: card)?.contentState(currentFingerprint: card.materialFingerprint)
    }

    func reviewContentState(for kit: Kit) -> ReviewContentState? {
        localReviewRecord(for: kit)?.contentState(currentFingerprint: kit.materialFingerprint)
    }

    /// Reviewed items whose material content has changed since sign-off. These
    /// stay reviewed and keep counting toward progress; the number exists only
    /// so the Review Center can offer an optional "worth a second look" list.
    func changedSinceReviewCount(
        procedures: [Procedure],
        rescueCards: [ComplicationRescueCard],
        kits: [Kit]
    ) -> Int {
        procedures.filter { hasMaterialChange(localReviewRecord(for: $0), fingerprint: $0.materialFingerprint) }.count
            + rescueCards.filter { hasMaterialChange(localReviewRecord(for: $0), fingerprint: $0.materialFingerprint) }.count
            + kits.filter { hasMaterialChange(localReviewRecord(for: $0), fingerprint: $0.materialFingerprint) }.count
    }

    func hasMaterialChange(_ record: LocalReviewRecord?, fingerprint: String) -> Bool {
        guard let record, record.disposition == .reviewed else { return false }
        return record.contentState(currentFingerprint: fingerprint) == .materialChanged
    }

    func clearReview(for procedure: Procedure) {
        clearLocalReviewDate(forKey: reviewKey(kind: "procedure", id: procedure.id))
    }

    func clearReview(for card: ComplicationRescueCard) {
        clearLocalReviewDate(forKey: reviewKey(kind: "rescue", id: card.id))
    }

    func clearReview(for kit: Kit) {
        clearLocalReviewDate(forKey: reviewKey(kind: "kit", id: kit.id))
    }

    func clearAllLocalReviews() {
        locallyReviewedContent = [:]
        saveLocallyReviewedContent()
    }

    func localReviewCount(procedures: [Procedure], rescueCards: [ComplicationRescueCard], kits: [Kit]) -> Int {
        procedures.filter { localReviewRecord(for: $0)?.disposition == .reviewed }.count
            + rescueCards.filter { localReviewRecord(for: $0)?.disposition == .reviewed }.count
            + kits.filter { localReviewRecord(for: $0)?.disposition == .reviewed }.count
    }

    func localReviewCount(disposition: LocalReviewDisposition, procedures: [Procedure], rescueCards: [ComplicationRescueCard], kits: [Kit]) -> Int {
        procedures.filter { localReviewRecord(for: $0)?.disposition == disposition }.count
            + rescueCards.filter { localReviewRecord(for: $0)?.disposition == disposition }.count
            + kits.filter { localReviewRecord(for: $0)?.disposition == disposition }.count
    }

    func pruneMissingProcedureData(validProcedureIDs: Set<String>) {
        let originalFavorites = favoriteIDs
        favoriteIDs = favoriteIDs.intersection(validProcedureIDs)
        if favoriteIDs != originalFavorites {
            saveFavorites()
        }

        let originalRecents = recentIDs
        recentIDs = recentIDs.filter { validProcedureIDs.contains($0) }
        if recentIDs != originalRecents {
            saveRecents()
        }

        let originalNoteKeys = Set(notes.keys)
        notes = notes.filter { validProcedureIDs.contains($0.key) }
        if Set(notes.keys) != originalNoteKeys {
            saveNotes()
        }

        let originalChecklistKeys = Set(checkedEquipment.keys)
        checkedEquipment = checkedEquipment.filter { validProcedureIDs.contains($0.key) }
        if Set(checkedEquipment.keys) != originalChecklistKeys {
            saveCheckedEquipment()
        }
    }

    /// Drops saved room-setup progress for kits that no longer exist. Keyed by
    /// kit ID (not procedure ID), so it must be pruned separately from the
    /// procedure-scoped data above, and only when kits actually loaded — never
    /// wipe a clinician's progress because a load transiently failed.
    func pruneMissingKitData(validKitIDs: Set<String>) {
        let originalKeys = Set(kitCheckedItems.keys)
        kitCheckedItems = kitCheckedItems.filter { validKitIDs.contains($0.key) }
        if Set(kitCheckedItems.keys) != originalKeys {
            saveKitCheckedItems()
        }
    }

    func reconcileLoadedContent(
        validProcedureIDs: Set<String>?,
        validRescueCardIDs: Set<String>?,
        validKitIDs: Set<String>?
    ) {
        if let validProcedureIDs {
            pruneMissingProcedureData(validProcedureIDs: validProcedureIDs)
        }
        if let validKitIDs {
            pruneMissingKitData(validKitIDs: validKitIDs)
        }
        pruneMissingReviewData(
            validProcedureIDs: validProcedureIDs,
            validRescueCardIDs: validRescueCardIDs,
            validKitIDs: validKitIDs
        )
    }

    func pruneMissingReviewData(
        validProcedureIDs: Set<String>?,
        validRescueCardIDs: Set<String>?,
        validKitIDs: Set<String>?
    ) {
        guard validProcedureIDs != nil || validRescueCardIDs != nil || validKitIDs != nil else {
            return
        }
        let originalKeys = Set(locallyReviewedContent.keys)
        locallyReviewedContent = locallyReviewedContent.filter { key, _ in
            let parts = key.split(separator: ":", maxSplits: 1).map(String.init)
            guard parts.count == 2 else { return false }

            switch parts[0] {
            case "procedure": return validProcedureIDs?.contains(parts[1]) ?? true
            case "rescue": return validRescueCardIDs?.contains(parts[1]) ?? true
            case "kit": return validKitIDs?.contains(parts[1]) ?? true
            default: return true
            }
        }
        if Set(locallyReviewedContent.keys) != originalKeys {
            saveLocallyReviewedContent()
        }
    }

    // MARK: - Bulk clearing (Settings)

    func clearRecents() {
        recentIDs = []
        saveRecents()
    }

    func clearFavorites() {
        favoriteIDs = []
        saveFavorites()
    }

    func clearAllNotes() {
        notes = [:]
        saveNotes()
    }

    func clearAllEquipment() {
        checkedEquipment = [:]
        saveCheckedEquipment()
    }

    func clearAllKitChecklists() {
        kitCheckedItems = [:]
        saveKitCheckedItems()
    }

    private func load() {
        if let favoriteArray = defaults.array(forKey: UserDataStoreKey.favorites) as? [String] {
            favoriteIDs = Set(favoriteArray)
        } else if let favoriteArray = defaults.array(forKey: UserDataStoreKey.legacyFavorites) as? [String] {
            favoriteIDs = Set(favoriteArray)
            saveFavorites()
        }

        if let recentArray = defaults.array(forKey: UserDataStoreKey.recents) as? [String] {
            recentIDs = Array(recentArray.prefix(AppConstants.maxRecents))
        } else if let recentArray = defaults.array(forKey: UserDataStoreKey.legacyRecents) as? [String] {
            recentIDs = Array(recentArray.prefix(AppConstants.maxRecents))
            saveRecents()
        }

        if let data = defaults.data(forKey: UserDataStoreKey.notes),
           let decoded = try? JSONDecoder().decode([String: String].self, from: data) {
            notes = decoded
        } else if let data = defaults.data(forKey: UserDataStoreKey.legacyNotes),
                  let decoded = try? JSONDecoder().decode([String: String].self, from: data) {
            notes = decoded
            saveNotes()
        }

        if let data = defaults.data(forKey: UserDataStoreKey.checkedEquipment),
           let decoded = try? JSONDecoder().decode([String: [String]].self, from: data) {
            checkedEquipment = decoded.mapValues { Set($0) }
        } else if let data = defaults.data(forKey: UserDataStoreKey.legacyCheckedEquipment),
                  let decoded = try? JSONDecoder().decode([String: [String]].self, from: data) {
            checkedEquipment = decoded.mapValues { Set($0) }
            saveCheckedEquipment()
        }

        if let data = defaults.data(forKey: UserDataStoreKey.kitCheckedItems),
           let decoded = try? JSONDecoder().decode([String: [String]].self, from: data) {
            kitCheckedItems = decoded.mapValues { Set($0) }
        }

        if let data = defaults.data(forKey: UserDataStoreKey.locallyReviewedContent),
           let decoded = try? JSONDecoder().decode([String: LocalReviewRecord].self, from: data) {
            locallyReviewedContent = decoded
        } else if let data = defaults.data(forKey: UserDataStoreKey.locallyReviewedContent),
                  let legacy = try? JSONDecoder().decode([String: String].self, from: data) {
            locallyReviewedContent = legacy.mapValues {
                LocalReviewRecord(disposition: .reviewed, date: $0)
            }
            saveLocallyReviewedContent()
        }
    }

    private func saveFavorites() {
        defaults.set(Array(favoriteIDs).sorted(), forKey: UserDataStoreKey.favorites)
    }

    private func saveRecents() {
        defaults.set(recentIDs, forKey: UserDataStoreKey.recents)
    }

    private func saveNotes() {
        do {
            let data = try JSONEncoder().encode(notes)
            defaults.set(data, forKey: UserDataStoreKey.notes)
        } catch {
            print("Failed to encode notes: \(error)")
        }
    }

    private func saveCheckedEquipment() {
        let encoded = checkedEquipment.mapValues { Array($0).sorted() }
        do {
            let data = try JSONEncoder().encode(encoded)
            defaults.set(data, forKey: UserDataStoreKey.checkedEquipment)
        } catch {
            print("Failed to encode checkedEquipment: \(error)")
        }
    }

    private func saveKitCheckedItems() {
        let encoded = kitCheckedItems.mapValues { Array($0).sorted() }
        do {
            let data = try JSONEncoder().encode(encoded)
            defaults.set(data, forKey: UserDataStoreKey.kitCheckedItems)
        } catch {
            print("Failed to encode kitCheckedItems: \(error)")
        }
    }

    private func saveLocallyReviewedContent() {
        do {
            let data = try JSONEncoder().encode(locallyReviewedContent)
            defaults.set(data, forKey: UserDataStoreKey.locallyReviewedContent)
        } catch {
            print("Failed to encode locallyReviewedContent: \(error)")
        }
    }

    private func setLocalReviewRecord(
        forKey key: String,
        disposition: LocalReviewDisposition,
        contentVersion: String,
        materialFingerprint: String
    ) {
        locallyReviewedContent[key] = LocalReviewRecord(
            disposition: disposition,
            date: Self.todayString(),
            contentVersion: contentVersion,
            materialFingerprint: materialFingerprint
        )
        saveLocallyReviewedContent()
    }

    private func clearLocalReviewDate(forKey key: String) {
        locallyReviewedContent.removeValue(forKey: key)
        saveLocallyReviewedContent()
    }

    private func reviewKey(kind: String, id: String) -> String {
        "\(kind):\(id)"
    }

    private static let formatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()

    private static func todayString(now: Date = Date()) -> String {
        return formatter.string(from: now)
    }
}

import Foundation

private enum UserDataStoreKey {
    static let favorites = "Procedures.favoriteIDs"
    static let recents = "Procedures.recentIDs"
    static let notes = "Procedures.notes"
    static let checkedEquipment = "Procedures.checkedEquipment"
    static let kitCheckedItems = "Procedures.kitCheckedItems"
    static let locallyReviewedContent = "Procedures.locallyReviewedContent"

    /// Appended to a key to hold bytes that failed to decode. See
    /// `UserDataStore.quarantine(_:forKey:)`.
    static let unreadableSuffix = ".unreadable"

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

    // MARK: - Review export

    static let reviewExportSchema = "procedures.local-reviews.v1"

    private struct ReviewExportPayload: Codable {
        let schema: String
        let exportedAt: String
        let reviews: [String: LocalReviewRecord]
    }

    /// Serializes local sign-offs for transfer back into the repo.
    ///
    /// Without this a review could never become the content's actual status: a
    /// clinician could work through all 73 items and every page would still
    /// read "AI draft — not clinically reviewed", because nothing carried the
    /// sign-off off the device. Paired with `scripts/apply_local_reviews.py`,
    /// which promotes reviewerStatus and provenance together.
    func exportReviewData() throws -> Data {
        let payload = ReviewExportPayload(
            schema: Self.reviewExportSchema,
            exportedAt: Self.todayString(),
            reviews: locallyReviewedContent
        )
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        return try encoder.encode(payload)
    }

    /// Writes the review export for sharing. Returns nil rather than trapping.
    func writeReviewExportFile() -> URL? {
        do {
            let data = try exportReviewData()
            let url = FileManager.default.temporaryDirectory
                .appendingPathComponent("procedure-reviews-\(Self.todayString()).json")
            try data.write(to: url, options: .atomic)
            return url
        } catch {
            print("Failed to write review export: \(error)")
            return nil
        }
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

    // MARK: - Effective review state

    /// The reconciled answer for one item. Every review surface in the app must
    /// route through here rather than reading `reviewer.isClinicallyReviewed`,
    /// which knows only what shipped and nothing about what the reader signed
    /// off on this device.
    func reviewState(for procedure: Procedure) -> ReviewState {
        ReviewState.resolve(
            sourceStatus: procedure.reviewer,
            record: localReviewRecord(for: procedure),
            contentState: reviewContentState(for: procedure)
        )
    }

    func reviewState(for card: ComplicationRescueCard) -> ReviewState {
        ReviewState.resolve(
            sourceStatus: card.reviewer,
            record: localReviewRecord(for: card),
            contentState: reviewContentState(for: card)
        )
    }

    func reviewState(for kit: Kit) -> ReviewState {
        ReviewState.resolve(
            sourceStatus: kit.reviewer,
            record: localReviewRecord(for: kit),
            contentState: reviewContentState(for: kit)
        )
    }

    /// Effective reviewed totals, counting bundled sign-offs and local ones
    /// without double-counting an item that has both.
    func effectiveReviewedCount(procedures: [Procedure]) -> Int {
        procedures.reduce(into: 0) { $0 += reviewState(for: $1).isReviewed ? 1 : 0 }
    }

    func effectiveReviewedCount(rescueCards: [ComplicationRescueCard]) -> Int {
        rescueCards.reduce(into: 0) { $0 += reviewState(for: $1).isReviewed ? 1 : 0 }
    }

    func effectiveReviewedCount(kits: [Kit]) -> Int {
        kits.reduce(into: 0) { $0 += reviewState(for: $1).isReviewed ? 1 : 0 }
    }

    /// Badge policy for a content kind, computed over the whole library.
    ///
    /// Deliberately not scoped to whatever subset a screen happens to be
    /// showing: if a filtered list of three could flip the policy, the same
    /// procedure would badge differently on two screens, and the badge would
    /// stop meaning anything.
    func badgePolicy(forProcedures procedures: [Procedure]) -> ReviewBadgePolicy {
        .make(reviewedCount: effectiveReviewedCount(procedures: procedures), total: procedures.count)
    }

    func badgePolicy(forRescueCards rescueCards: [ComplicationRescueCard]) -> ReviewBadgePolicy {
        .make(reviewedCount: effectiveReviewedCount(rescueCards: rescueCards), total: rescueCards.count)
    }

    func badgePolicy(forKits kits: [Kit]) -> ReviewBadgePolicy {
        .make(reviewedCount: effectiveReviewedCount(kits: kits), total: kits.count)
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

    /// Blobs that could not be decoded this launch. Their bytes are preserved
    /// under a `.unreadable` sidecar key, and this drives the notice that says
    /// so — because the alternative is that the loss is never mentioned.
    @Published private(set) var unreadableDataKeys: Set<String> = []

    /// Preserves a blob we could not decode, before anything overwrites it.
    ///
    /// Every collection here is stored as one whole-blob key and saved by
    /// rewriting that blob entirely. So a single undecodable record — a
    /// renamed disposition raw value, a field that stopped being optional,
    /// a truncated write — left the collection empty in memory, and the very
    /// next sign-off wrote one record over all of them. Nothing crashed and
    /// nothing logged; the Review Center just read 1 of 73 instead of 48.
    ///
    /// Refusing to write at all would have been the other obvious answer, and
    /// it is worse: it makes the app unable to record a review for as long as
    /// the bad blob exists. Keeping the original bytes makes the loss
    /// recoverable, and `unreadableDataKeys` makes it visible.
    private func quarantine(_ data: Data, forKey key: String) {
        let sidecar = key + UserDataStoreKey.unreadableSuffix
        // Never overwrite an existing quarantine — that would destroy the
        // original copy on the second bad launch, which is the one case this
        // whole mechanism exists to survive.
        if defaults.data(forKey: sidecar) == nil {
            defaults.set(data, forKey: sidecar)
        }
        unreadableDataKeys.insert(key)
    }

    /// Whether any saved data failed to load and was set aside.
    var hasUnreadableData: Bool { !unreadableDataKeys.isEmpty }

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

        if let data = defaults.data(forKey: UserDataStoreKey.notes) {
            if let decoded = try? JSONDecoder().decode([String: String].self, from: data) {
                notes = decoded
            } else {
                quarantine(data, forKey: UserDataStoreKey.notes)
            }
        } else if let data = defaults.data(forKey: UserDataStoreKey.legacyNotes),
                  let decoded = try? JSONDecoder().decode([String: String].self, from: data) {
            notes = decoded
            saveNotes()
        }

        if let data = defaults.data(forKey: UserDataStoreKey.checkedEquipment) {
            if let decoded = try? JSONDecoder().decode([String: [String]].self, from: data) {
                checkedEquipment = decoded.mapValues { Set($0) }
            } else {
                quarantine(data, forKey: UserDataStoreKey.checkedEquipment)
            }
        } else if let data = defaults.data(forKey: UserDataStoreKey.legacyCheckedEquipment),
                  let decoded = try? JSONDecoder().decode([String: [String]].self, from: data) {
            checkedEquipment = decoded.mapValues { Set($0) }
            saveCheckedEquipment()
        }

        if let data = defaults.data(forKey: UserDataStoreKey.kitCheckedItems) {
            if let decoded = try? JSONDecoder().decode([String: [String]].self, from: data) {
                kitCheckedItems = decoded.mapValues { Set($0) }
            } else {
                quarantine(data, forKey: UserDataStoreKey.kitCheckedItems)
            }
        }

        if let data = defaults.data(forKey: UserDataStoreKey.locallyReviewedContent) {
            if let decoded = try? JSONDecoder().decode([String: LocalReviewRecord].self, from: data) {
                locallyReviewedContent = decoded
            } else if let legacy = try? JSONDecoder().decode([String: String].self, from: data) {
                // Pre-record format: a bare date string per key.
                locallyReviewedContent = legacy.mapValues {
                    LocalReviewRecord(disposition: .reviewed, date: $0)
                }
                saveLocallyReviewedContent()
            } else {
                // The sign-offs are the one collection that cannot be
                // reconstructed by using the app normally, so losing this blob
                // silently is the worst case the quarantine exists for.
                quarantine(data, forKey: UserDataStoreKey.locallyReviewedContent)
            }
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

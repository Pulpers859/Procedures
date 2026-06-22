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

@MainActor
final class UserDataStore: ObservableObject {
    @Published private(set) var favoriteIDs: Set<String> = []
    @Published private(set) var recentIDs: [String] = []
    @Published private(set) var notes: [String: String] = [:]
    @Published private(set) var checkedEquipment: [String: Set<String>] = [:]
    @Published private(set) var kitCheckedItems: [String: Set<String>] = [:]
    @Published private(set) var locallyReviewedContent: [String: String] = [:]

    init() {
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
        checkedEquipment[procedure.id] = []
        saveCheckedEquipment()
    }

    // MARK: - Kit checklist

    func isKitItemChecked(_ item: String, forKitID kitID: String) -> Bool {
        kitCheckedItems[kitID, default: []].contains(item)
    }

    func toggleKitItem(_ item: String, forKitID kitID: String) {
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
        kitCheckedItems[kitID] = []
        saveKitCheckedItems()
    }

    // MARK: - Local review status

    func localReviewDate(for procedure: Procedure) -> String? {
        locallyReviewedContent[reviewKey(kind: "procedure", id: procedure.id)]
    }

    func localReviewDate(for card: ComplicationRescueCard) -> String? {
        locallyReviewedContent[reviewKey(kind: "rescue", id: card.id)]
    }

    func localReviewDate(for kit: Kit) -> String? {
        locallyReviewedContent[reviewKey(kind: "kit", id: kit.id)]
    }

    func markReviewed(_ procedure: Procedure) {
        setLocalReviewDate(forKey: reviewKey(kind: "procedure", id: procedure.id))
    }

    func markReviewed(_ card: ComplicationRescueCard) {
        setLocalReviewDate(forKey: reviewKey(kind: "rescue", id: card.id))
    }

    func markReviewed(_ kit: Kit) {
        setLocalReviewDate(forKey: reviewKey(kind: "kit", id: kit.id))
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
        procedures.filter { localReviewDate(for: $0) != nil }.count
            + rescueCards.filter { localReviewDate(for: $0) != nil }.count
            + kits.filter { localReviewDate(for: $0) != nil }.count
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

    func pruneMissingReviewData(validProcedureIDs: Set<String>, validRescueCardIDs: Set<String>, validKitIDs: Set<String>) {
        let originalKeys = Set(locallyReviewedContent.keys)
        locallyReviewedContent = locallyReviewedContent.filter { key, _ in
            let parts = key.split(separator: ":", maxSplits: 1).map(String.init)
            guard parts.count == 2 else { return false }

            switch parts[0] {
            case "procedure": return validProcedureIDs.contains(parts[1])
            case "rescue": return validRescueCardIDs.contains(parts[1])
            case "kit": return validKitIDs.contains(parts[1])
            default: return false
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
        let defaults = UserDefaults.standard

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
           let decoded = try? JSONDecoder().decode([String: String].self, from: data) {
            locallyReviewedContent = decoded
        }
    }

    private func saveFavorites() {
        UserDefaults.standard.set(Array(favoriteIDs).sorted(), forKey: UserDataStoreKey.favorites)
    }

    private func saveRecents() {
        UserDefaults.standard.set(recentIDs, forKey: UserDataStoreKey.recents)
    }

    private func saveNotes() {
        if let data = try? JSONEncoder().encode(notes) {
            UserDefaults.standard.set(data, forKey: UserDataStoreKey.notes)
        }
    }

    private func saveCheckedEquipment() {
        let encoded = checkedEquipment.mapValues { Array($0).sorted() }
        if let data = try? JSONEncoder().encode(encoded) {
            UserDefaults.standard.set(data, forKey: UserDataStoreKey.checkedEquipment)
        }
    }

    private func saveKitCheckedItems() {
        let encoded = kitCheckedItems.mapValues { Array($0).sorted() }
        if let data = try? JSONEncoder().encode(encoded) {
            UserDefaults.standard.set(data, forKey: UserDataStoreKey.kitCheckedItems)
        }
    }

    private func saveLocallyReviewedContent() {
        if let data = try? JSONEncoder().encode(locallyReviewedContent) {
            UserDefaults.standard.set(data, forKey: UserDataStoreKey.locallyReviewedContent)
        }
    }

    private func setLocalReviewDate(forKey key: String) {
        locallyReviewedContent[key] = Self.todayString()
        saveLocallyReviewedContent()
    }

    private func clearLocalReviewDate(forKey key: String) {
        locallyReviewedContent.removeValue(forKey: key)
        saveLocallyReviewedContent()
    }

    private func reviewKey(kind: String, id: String) -> String {
        "\(kind):\(id)"
    }

    private static func todayString(now: Date = Date()) -> String {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone.current
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter.string(from: now)
    }
}

import Foundation

private enum UserDataStoreKey {
    static let favorites = "Procedures.favoriteIDs"
    static let recents = "Procedures.recentIDs"
    static let notes = "Procedures.notes"
    static let checkedEquipment = "Procedures.checkedEquipment"

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
}

import Foundation
#if canImport(Security)
import Security
#endif

enum CaseMentorCredentialStore {
    private static let service = "Procedures.CaseMentor"
    private static let account = "OpenAIAPIKey"

    static func loadAPIKey() -> String {
        #if canImport(Security)
        var query = baseQuery()
        query[kSecReturnData as String] = true
        query[kSecMatchLimit as String] = kSecMatchLimitOne

        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)
        guard status == errSecSuccess,
              let data = item as? Data,
              let key = String(data: data, encoding: .utf8) else {
            return ""
        }
        return key
        #else
        return ""
        #endif
    }

    static func saveAPIKey(_ apiKey: String) {
        #if canImport(Security)
        let trimmed = apiKey.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            deleteAPIKey()
            return
        }

        let data = Data(trimmed.utf8)
        var query = baseQuery()
        let attributes: [String: Any] = [
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]

        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        if status == errSecItemNotFound {
            query[kSecValueData as String] = data
            query[kSecAttrAccessible as String] = kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
            SecItemAdd(query as CFDictionary, nil)
        }
        #endif
    }

    static func deleteAPIKey() {
        #if canImport(Security)
        SecItemDelete(baseQuery() as CFDictionary)
        #endif
    }

    private static func baseQuery() -> [String: Any] {
        #if canImport(Security)
        return [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account
        ]
        #else
        return [:]
        #endif
    }
}

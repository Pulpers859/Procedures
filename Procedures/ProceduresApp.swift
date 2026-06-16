import SwiftUI

enum AppConstants {
    static let maxRecents = 12

    static let clinicalDisclaimer = "Procedures is for rapid educational review by trained clinicians. It does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy."

    static let shortDisclaimer = "Educational review for trained clinicians. Does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy."

    static var appVersionDescription: String {
        let info = Bundle.main.infoDictionary
        let version = info?["CFBundleShortVersionString"] as? String ?? "Unknown"
        let build = info?["CFBundleVersion"] as? String ?? ""
        return build.isEmpty ? version : "\(version) (\(build))"
    }
}

@main
struct ProceduresApp: App {
    @StateObject private var repository = ProcedureRepository()
    @StateObject private var userData = UserDataStore()

    var body: some Scene {
        WindowGroup {
            RootTabView()
                .environmentObject(repository)
                .environmentObject(userData)
        }
    }
}

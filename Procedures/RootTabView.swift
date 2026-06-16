import SwiftUI

private enum RootTabStorageKey {
    static let disclaimerAccepted = "Procedures.hasAcceptedClinicalDisclaimer"
    static let legacyDisclaimerAccepted = "ProcedureSTAT.hasAcceptedClinicalDisclaimer"
}

struct RootTabView: View {
    @AppStorage(RootTabStorageKey.disclaimerAccepted) private var hasAcceptedClinicalDisclaimer = false
    @AppStorage(SettingsStorageKey.appearance) private var appearanceRaw = AppAppearance.system.rawValue

    private var appearance: AppAppearance {
        AppAppearance(rawValue: appearanceRaw) ?? .system
    }

    init() {
        let defaults = UserDefaults.standard
        if defaults.object(forKey: RootTabStorageKey.disclaimerAccepted) == nil,
           defaults.object(forKey: RootTabStorageKey.legacyDisclaimerAccepted) != nil {
            defaults.set(
                defaults.bool(forKey: RootTabStorageKey.legacyDisclaimerAccepted),
                forKey: RootTabStorageKey.disclaimerAccepted
            )
        }
    }

    var body: some View {
        TabView {
            GuideHomeView()
                .tabItem { Label("Guide", systemImage: "sparkles.rectangle.stack") }

            ProcedureListView()
                .tabItem { Label("Procedures", systemImage: "list.bullet.rectangle") }

            ComplicationsHomeView()
                .tabItem { Label("Rescue", systemImage: "lifepreserver.fill") }

            KitsHomeView()
                .tabItem { Label("Kits", systemImage: "checklist.checked") }

            SavedView()
                .tabItem { Label("Saved", systemImage: "bookmark.fill") }
        }
        .tint(.blue)
        .preferredColorScheme(appearance.colorScheme)
        .alert("Clinical Review Tool", isPresented: Binding(
            get: { !hasAcceptedClinicalDisclaimer },
            set: { newValue in
                if newValue == false { hasAcceptedClinicalDisclaimer = true }
            }
        )) {
            Button("I Understand", role: .cancel) {
                hasAcceptedClinicalDisclaimer = true
            }
        } message: {
            Text("Procedures is for rapid educational review by trained clinicians. It does not replace formal training, supervision, credentialing, clinical judgment, or local institutional policy.")
        }
    }
}

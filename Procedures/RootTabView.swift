import SwiftUI

private enum RootTabStorageKey {
    static let disclaimerAccepted = "Procedures.hasAcceptedClinicalDisclaimer"
    static let legacyDisclaimerAccepted = "ProcedureSTAT.hasAcceptedClinicalDisclaimer"
}

struct RootTabView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
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

            EquipmentHomeView()
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
            Text(AppConstants.clinicalDisclaimer)
        }
        .onAppear {
            guard !repository.procedures.isEmpty else { return }
            userData.pruneMissingProcedureData(validProcedureIDs: Set(repository.procedures.map(\.id)))
        }
    }
}

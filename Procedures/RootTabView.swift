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
        .fullScreenCover(isPresented: Binding(
            get: { !hasAcceptedClinicalDisclaimer },
            set: { newValue in
                if newValue == false { hasAcceptedClinicalDisclaimer = true }
            }
        )) {
            DisclaimerView {
                hasAcceptedClinicalDisclaimer = true
            }
        }
        .onAppear {
            guard !repository.procedures.isEmpty else { return }
            userData.pruneMissingProcedureData(validProcedureIDs: Set(repository.procedures.map(\.id)))
        }
    }
}

private struct DisclaimerView: View {
    let onAccept: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            Spacer()

            VStack(spacing: 24) {
                Image(systemName: "cross.case.fill")
                    .font(.system(size: 48))
                    .foregroundStyle(.blue)

                Text("Clinical Review Tool")
                    .font(.title2.weight(.bold))

                Text(AppConstants.clinicalDisclaimer)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal, 32)

            Spacer()

            Button(action: onAccept) {
                Text("I Understand")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.borderedProminent)
            .padding(.horizontal, 32)
            .padding(.bottom, 48)
        }
        .background(Color(.systemBackground))
        .interactiveDismissDisabled()
    }
}

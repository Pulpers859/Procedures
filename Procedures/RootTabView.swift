import SwiftUI
import CoreSpotlight

private enum RootTabStorageKey {
    static let disclaimerAccepted = "Procedures.hasAcceptedClinicalDisclaimer"
    static let legacyDisclaimerAccepted = "ProcedureSTAT.hasAcceptedClinicalDisclaimer"
}

private enum RootTab: String, Hashable {
    case guide
    case procedures
    case rescue
    case kits
    case saved
}

struct RootTabView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @EnvironmentObject private var editStore: ProcedureEditStore
    @ObservedObject private var deepLinkRouter = DeepLinkRouter.shared
    @AppStorage(RootTabStorageKey.disclaimerAccepted) private var hasAcceptedClinicalDisclaimer = false
    @AppStorage(SettingsStorageKey.appearance) private var appearanceRaw = AppAppearance.system.rawValue
    @SceneStorage("Procedures.selectedRootTab") private var selectedTabRaw = RootTab.guide.rawValue

    private var appearance: AppAppearance {
        AppAppearance(rawValue: appearanceRaw) ?? .system
    }

    private var selectedTab: Binding<RootTab> {
        Binding(
            get: { RootTab(rawValue: selectedTabRaw) ?? .guide },
            set: { selectedTabRaw = $0.rawValue }
        )
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
        TabView(selection: selectedTab) {
            GuideHomeView()
                // "Guide" named the content; the screen is a dispatcher, and
                // the first complaint about it was that it did not feel like a
                // home screen.
                .tabItem { Label("Home", systemImage: "house.fill") }
                .tag(RootTab.guide)

            ProcedureListView()
                .tabItem { Label("Procedures", systemImage: "list.bullet.rectangle") }
                .tag(RootTab.procedures)

            ComplicationsHomeView()
                .tabItem { Label("Rescue", systemImage: "lifepreserver.fill") }
                .tag(RootTab.rescue)

            KitsHomeView()
                .tabItem { Label("Kits", systemImage: "checklist.checked") }
                .tag(RootTab.kits)

            SavedView()
                .tabItem { Label("Saved", systemImage: "bookmark.fill") }
                .tag(RootTab.saved)
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
        .onContinueUserActivity(CSSearchableItemActionType) { activity in
            if let identifier = activity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
                deepLinkRouter.openSpotlightItem(identifier: identifier)
            }
        }
        .onChange(of: deepLinkRouter.destination) { _, destination in
            routeDeepLink(destination)
        }
        .onAppear {
            // Overlay local edits before anything reads content, so Spotlight
            // and the search index publish the corrected text.
            repository.attachEditStore(editStore)
            routeDeepLink(deepLinkRouter.destination)
            reindexSpotlight()
            let procedureIDs = ContentLoadAuthority.authoritativeIDs(
                Set(repository.procedures.map(\.id)),
                loadError: repository.loadError,
                loadWarning: repository.loadWarning
            )
            let rescueCardIDs = ContentLoadAuthority.authoritativeIDs(
                Set(repository.rescueCards.map(\.id)),
                loadError: repository.rescueLoadError,
                loadWarning: repository.rescueLoadWarning
            )
            let kitIDs = ContentLoadAuthority.authoritativeIDs(
                Set(repository.kits.map(\.id)),
                loadError: repository.kitLoadError,
                loadWarning: repository.kitLoadWarning
            )

            userData.reconcileLoadedContent(
                validProcedureIDs: procedureIDs,
                validRescueCardIDs: rescueCardIDs,
                validKitIDs: kitIDs
            )
            // Only prune edits when the bundled load was complete; a transient
            // failure must never delete a clinician's corrections.
            if let procedureIDs {
                editStore.pruneMissingProcedures(validProcedureIDs: procedureIDs)
            }
        }
        // Spotlight was indexed only at launch, so a correction made on shift
        // did not reach it until the next cold start. The crash path is exactly
        // where a clinician searches from outside the app, and serving them the
        // text they had already fixed is the failure this app exists to avoid.
        .onChange(of: editStore.editsByProcedureID) { _, _ in
            reindexSpotlight()
        }
    }

    private func reindexSpotlight() {
        SpotlightIndexer.reindex(
            procedures: repository.procedures,
            rescueCards: repository.rescueCards
        )
    }

    /// Tab-level routing for external activations. The destination stays
    /// pending on the router so the destination tab's view can finish the
    /// route (push the card/procedure) and then clear it.
    private func routeDeepLink(_ destination: DeepLinkRouter.Destination?) {
        switch destination {
        case .rescueTab:
            selectedTabRaw = RootTab.rescue.rawValue
            deepLinkRouter.destination = nil
        case .rescueCard:
            selectedTabRaw = RootTab.rescue.rawValue
        case .procedure:
            selectedTabRaw = RootTab.procedures.rawValue
        case nil:
            break
        }
    }
}

private struct DisclaimerView: View {
    let onAccept: () -> Void

    var body: some View {
        ScrollView {
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
            .padding(.vertical, 48)
            .frame(maxWidth: .infinity)
        }
        .safeAreaInset(edge: .bottom) {
            Button(action: onAccept) {
                Text("I Understand")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
            }
            .buttonStyle(.borderedProminent)
            .padding(.horizontal, 32)
            .padding(.vertical, 12)
            .background(.bar)
        }
        .background(Color(.systemBackground))
        .interactiveDismissDisabled()
    }
}

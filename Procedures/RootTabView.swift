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
    @EnvironmentObject private var recoveryStore: ClinicalRecoveryStore
    @ObservedObject private var deepLinkRouter = DeepLinkRouter.shared
    @Environment(\.scenePhase) private var scenePhase
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

    // Split out of `body` deliberately. The recovery-backup work added seven
    // chained autosave `.onChange` modifiers, and stacked on the five-tab
    // TabView plus the disclaimer cover, Spotlight handling and the
    // scene-phase hook, the single expression went past what the Swift type
    // checker will solve: the build failed with "unable to type-check this
    // expression in reasonable time". Each computed property and modifier
    // below gives the compiler a scope it can close on its own.
    private var tabs: some View {
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
    }

    var body: some View {
        tabs
            .tint(.blue)
            .preferredColorScheme(appearance.colorScheme)
            .modifier(DisclaimerGate(hasAccepted: $hasAcceptedClinicalDisclaimer))
            .modifier(
                AutomaticRecoverySnapshots(
                    userData: userData,
                    editStore: editStore,
                    recoveryStore: recoveryStore,
                    onEditsChanged: reindexSpotlight
                )
            )
            .onContinueUserActivity(CSSearchableItemActionType) { activity in
                if let identifier = activity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
                    deepLinkRouter.openSpotlightItem(identifier: identifier)
                }
            }
            .onChange(of: deepLinkRouter.destination) { _, destination in
                routeDeepLink(destination)
            }
            .onAppear(perform: handleAppear)
            // A checklist session belongs to the case in front of the reader.
            // The active-session sets used to be cleared only by constructing
            // the store — a cold launch — and iOS keeps an app resident for
            // days, so ticks from a previous case could reappear as the
            // current room's state with no confirmation.
            .onChange(of: scenePhase) { _, phase in
                if phase == .background {
                    userData.endActiveChecklistSessions()
                    recoveryStore.snapshotNow(userData: userData, editStore: editStore)
                }
            }
    }

    private func handleAppear() {
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

/// The clinical-disclaimer gate, lifted out of `RootTabView.body`.
///
/// A `Binding` rather than the `@AppStorage` itself so the cover's presentation
/// state and the stored acceptance stay one value: dismissing by any route is
/// the same as accepting, which is what the original inline binding encoded.
@MainActor
private struct DisclaimerGate: ViewModifier {
    @Binding var hasAccepted: Bool

    func body(content: Content) -> some View {
        content.fullScreenCover(
            isPresented: Binding(
                get: { !hasAccepted },
                set: { newValue in
                    if newValue == false { hasAccepted = true }
                }
            )
        ) {
            DisclaimerView { hasAccepted = true }
        }
    }
}

/// Every local-data change that should trigger a recovery snapshot.
///
/// These were seven near-identical `.onChange` modifiers chained directly onto
/// `RootTabView.body`; together with the rest of the chain they are what broke
/// the type checker. Bundling them gives the compiler a separate scope to
/// solve and puts the repeated `scheduleAutomaticSnapshot` call in one place,
/// so a future published property cannot be wired up subtly differently from
/// its six neighbours.
/// `@MainActor` because `snapshot()` below is a plain helper that calls into
/// the `@MainActor`-isolated stores. Without it that call is a hard isolation
/// error — the same class of break that took this build down twice already.
@MainActor
private struct AutomaticRecoverySnapshots: ViewModifier {
    @ObservedObject var userData: UserDataStore
    @ObservedObject var editStore: ProcedureEditStore
    @ObservedObject var recoveryStore: ClinicalRecoveryStore
    /// Spotlight was indexed only at launch, so a correction made on shift did
    /// not reach it until the next cold start. The crash path is exactly where
    /// a clinician searches from outside the app, and serving them the text
    /// they had already fixed is the failure this app exists to avoid.
    let onEditsChanged: () -> Void

    func body(content: Content) -> some View {
        content
            .onChange(of: editStore.editsByProcedureID) { _, _ in
                onEditsChanged()
                snapshot()
            }
            .onChange(of: userData.favoriteIDs) { _, _ in snapshot() }
            .onChange(of: userData.recentIDs) { _, _ in snapshot() }
            .onChange(of: userData.notes) { _, _ in snapshot() }
            .onChange(of: userData.checkedEquipment) { _, _ in snapshot() }
            .onChange(of: userData.kitCheckedItems) { _, _ in snapshot() }
            .onChange(of: userData.locallyReviewedContent) { _, _ in snapshot() }
    }

    private func snapshot() {
        recoveryStore.scheduleAutomaticSnapshot(userData: userData, editStore: editStore)
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

import SwiftUI

/// The app's home screen: a dispatcher, not a catalogue.
///
/// This screen used to render four `.insetGrouped` sections of identical visual
/// weight — rescue, recents, pathways, and every one of the 37 advanced and
/// rare-crash procedures. Three of the four duplicated another tab (two under
/// the same section title), which left the one thing only this screen does —
/// pathway routing — buried in third place. With everything emphasised nothing
/// was, and the screen read as a list of lists rather than a home.
///
/// The structure now has three deliberate weight tiers: one rescue signpost,
/// the pathway grid, and a quiet strip of recents. The library itself lives in
/// the Procedures tab, where a high-risk filter replaces the old dump.
struct GuideHomeView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize
    @State private var searchText = ""
    @State private var selectedPathway: ClinicalPathway?

    private var filteredProcedures: [Procedure] {
        repository.search(searchText)
    }

    private var filteredRescueCards: [ComplicationRescueCard] {
        repository.searchRescueCards(searchText)
    }

    private var filteredKits: [Kit] {
        repository.searchKits(searchText)
    }

    /// Hard cap. An unbounded section turns a dashboard into a feed: the screen
    /// changes shape as the app is used, so no muscle memory can form.
    private var recentProcedures: [Procedure] {
        Array(userData.recentIDs.compactMap { repository.procedure(withID: $0) }.prefix(3))
    }

    var body: some View {
        NavigationStack {
            Group {
                if searchText.isEmpty {
                    browseHome
                } else {
                    List { searchResults }
                        .listStyle(.insetGrouped)
                }
            }
            .background(Color(.systemGroupedBackground))
            .navigationTitle("Home")
            .settingsToolbar()
            // Placement matches every other tab. A pinned drawer kept the field
            // on screen permanently with no way to push it away, which is worse
            // than the scroll it was meant to save.
            .searchable(text: $searchText, prompt: "Search procedure, problem, or kit…")
            .scrollDismissesKeyboard(.immediately)
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
            }
            .navigationDestination(item: $selectedPathway) { pathway in
                PathwayProcedureListView(pathway: pathway)
            }
        }
    }

    // MARK: - Home

    private var browseHome: some View {
        ScrollView {
            LazyVStack(alignment: .leading, spacing: 28) {
                rescueHero

                libraryHealthNotice

                pathwaySection

                if !recentProcedures.isEmpty {
                    recentSection
                }
            }
            .detailContentColumn()
            .padding(.horizontal, 16)
            .padding(.top, 12)
            .padding(.bottom, 28)
        }
    }

    /// The single loud element on this screen.
    ///
    /// It is deliberately not the crash path — the Rescue tab is, being fixed
    /// in the thumb's arc and one tap from anywhere. This is signage for it:
    /// unmissable, and recognisable as a blur without reading a word.
    ///
    /// Red appears exactly once on this screen and nowhere else on it. Red that
    /// is used indiscriminately stops being read, and these users are trained on
    /// alarm hierarchies every shift.
    @ViewBuilder
    private var rescueHero: some View {
        if let error = repository.rescueLoadError {
            RescueHeroCard(
                title: "Rescue cards unavailable",
                subtitle: error,
                isActionable: false
            )
        } else if repository.rescueCards.isEmpty {
            RescueHeroCard(
                title: "Rescue cards unavailable",
                subtitle: "No rescue content loaded.",
                isActionable: false
            )
        } else {
            NavigationLink {
                AllRescueCardsListView()
            } label: {
                RescueHeroCard(
                    title: "Something's going wrong",
                    subtitle: "Rescue cards — immediate steps",
                    isActionable: true
                )
            }
            .buttonStyle(.plain)
        }
    }

    /// Says so when the library did not load.
    ///
    /// This screen read `rescueLoadError` and nothing else. If procedures.json
    /// failed to decode, Home rendered normally: a working rescue hero and a
    /// pathway grid where every tile read "0". No error anywhere. Tapping a
    /// pathway then reassured the reader that the emptiness was deliberate
    /// ("Content is added before release rather than showing empty
    /// categories"), and searching blamed the query. Three screens agreeing
    /// that a failed library was fine.
    ///
    /// The rescue hero stays the loud element — it is the crash path, and it
    /// may still work when the library does not. These sit under it, in the
    /// warning tone rather than red.
    @ViewBuilder
    private var libraryHealthNotice: some View {
        let notices: [(String, String)] = [
            repository.loadError.map { ("Procedures unavailable", $0) },
            repository.loadWarning.map { ("Some procedures were skipped", $0) },
            repository.kitLoadError.map { ("Kits unavailable", $0) },
            repository.kitLoadWarning.map { ("Some kits were skipped", $0) },
            userData.hasUnreadableData
                ? ("Saved data could not be read",
                   "Some saved reviews or notes could not be read and were set aside rather than overwritten. Recorded work from this point is saved normally.")
                : nil
        ].compactMap { $0 }

        if !notices.isEmpty {
            VStack(alignment: .leading, spacing: 12) {
                ForEach(notices, id: \.0) { title, message in
                    Label {
                        VStack(alignment: .leading, spacing: 2) {
                            Text(title).font(.subheadline.weight(.semibold))
                            Text(message).font(.footnote).foregroundStyle(.secondary)
                        }
                    } icon: {
                        Image(systemName: "exclamationmark.triangle.fill")
                    }
                    .foregroundStyle(AppSemanticColor.warningText)
                    .fixedSize(horizontal: false, vertical: true)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .accessibilityElement(children: .combine)
                }
            }
            .padding(14)
            .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
        }
    }

    private var pathwaySection: some View {
        VStack(alignment: .leading, spacing: 12) {
            sectionHeading("Clinical Pathways")

            LazyVGrid(columns: pathwayColumns, spacing: 12) {
                ForEach(ClinicalPathway.defaultPathways) { pathway in
                    Button {
                        selectedPathway = pathway
                    } label: {
                        PathwayTile(pathway: pathway, count: pathwayCount(pathway))
                    }
                    .buttonStyle(.plain)
                    // Leaving List costs the free accessibility grouping it
                    // provided, so every custom control states its own label
                    // and traits.
                    .accessibilityElement(children: .combine)
                    .accessibilityLabel("\(pathway.title), \(pathwayCount(pathway)) procedures")
                    .accessibilityHint(pathway.subtitle)
                    .accessibilityAddTraits(.isButton)
                }
            }
        }
    }

    private var recentSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            sectionHeading("Pick Up Where You Left Off")

            VStack(spacing: 0) {
                ForEach(Array(recentProcedures.enumerated()), id: \.element.id) { index, procedure in
                    if index > 0 {
                        Divider().padding(.leading, 14)
                    }
                    NavigationLink(value: procedure) {
                        HStack(spacing: 10) {
                            Text(procedure.title)
                                .font(.subheadline)
                                .foregroundStyle(.primary)
                                .lineLimit(2)
                                .fixedSize(horizontal: false, vertical: true)
                            Spacer(minLength: 8)
                            Image(systemName: "chevron.right")
                                .font(.caption.weight(.semibold))
                                .foregroundStyle(.tertiary)
                        }
                        .padding(.horizontal, 14)
                        .frame(minHeight: AppLayout.controlMinHeight, alignment: .leading)
                        .contentShape(Rectangle())
                    }
                    .buttonStyle(.plain)
                    .accessibilityAddTraits(.isButton)
                }
            }
            .background(
                Color(.secondarySystemGroupedBackground),
                in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
            )
        }
    }

    private func sectionHeading(_ title: String) -> some View {
        Text(title)
            .font(.title3.weight(.bold))
            .foregroundStyle(.primary)
            .accessibilityAddTraits(.isHeader)
    }

    private var pathwayColumns: [GridItem] {
        if dynamicTypeSize.isAccessibilitySize {
            return [GridItem(.flexible())]
        }
        return [GridItem(.flexible(), spacing: 12), GridItem(.flexible(), spacing: 12)]
    }

    private func pathwayCount(_ pathway: ClinicalPathway) -> Int {
        repository.procedures.filter { pathway.categories.contains($0.category) }.count
    }

    // MARK: - Search

    @ViewBuilder
    private var searchResults: some View {
        if filteredRescueCards.isEmpty && filteredProcedures.isEmpty && filteredKits.isEmpty {
            Section {
                // Blaming the query is only honest when there was something to
                // search. With a failed load this said "Try a procedure name"
                // about a library that was not there.
                if repository.loadError != nil || repository.procedures.isEmpty {
                    EmptyStateView(
                        title: "Content unavailable",
                        message: repository.loadError ?? "The procedure library did not load, so there is nothing to search.",
                        systemImage: "exclamationmark.triangle"
                    )
                } else {
                    EmptyStateView(
                        title: "No results",
                        message: "Try a procedure, clinical problem, abbreviation, or kit name.",
                        systemImage: "magnifyingglass"
                    )
                }
            }
        } else if !filteredRescueCards.isEmpty {
            Section("Rescue Cards") {
                ForEach(filteredRescueCards) { card in
                    NavigationLink(value: card) {
                        RescueCardRow(card: card)
                    }
                }
            }
        }

        if !filteredProcedures.isEmpty {
            Section("Procedures") {
                ForEach(filteredProcedures) { procedure in
                    NavigationLink(value: procedure) {
                        ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                    }
                }
            }
        }

        if !filteredKits.isEmpty {
            Section("Kits") {
                ForEach(filteredKits) { kit in
                    NavigationLink(value: kit) {
                        VStack(alignment: .leading, spacing: 3) {
                            Text(kit.title)
                                .font(.headline)
                            Text(kit.subtitle)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)
                                .lineLimit(2)
                        }
                    }
                }
            }
        }
    }
}

/// The rescue signpost.
///
/// Differentiated by silhouette before hue: it is the only full-bleed, tall,
/// single-purpose object on the screen, so it survives both attentional
/// narrowing under stress and colour-vision deficiency. Colour is never the
/// only signal — the glyph and the words carry the same meaning.
struct RescueHeroCard: View {
    let title: String
    let subtitle: String
    let isActionable: Bool

    /// Scaled, never fixed: a hard height clips this card at accessibility
    /// text sizes, and this is the last thing on the screen that may break.
    @ScaledMetric(relativeTo: .title2) private var minHeight: CGFloat = 96
    @ScaledMetric(relativeTo: .title2) private var glyphSize: CGFloat = 46
    @Environment(\.accessibilityDifferentiateWithoutColor) private var differentiateWithoutColor

    private var accent: Color { isActionable ? .red : .orange }

    var body: some View {
        HStack(spacing: 14) {
            Image(systemName: isActionable ? "lifepreserver.fill" : "exclamationmark.triangle.fill")
                .font(.title.weight(.semibold))
                .foregroundStyle(.white)
                .frame(width: glyphSize, height: glyphSize)
                .background(accent, in: RoundedRectangle(cornerRadius: 14, style: .continuous))

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.title3.weight(.bold))
                    .foregroundStyle(.primary)
                    .fixedSize(horizontal: false, vertical: true)
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }

            Spacer(minLength: 4)

            if isActionable {
                Image(systemName: "chevron.right")
                    .font(.subheadline.weight(.bold))
                    .foregroundStyle(accent)
            }
        }
        .padding(16)
        .frame(maxWidth: .infinity, minHeight: minHeight, alignment: .leading)
        .background(accent.opacity(0.10), in: RoundedRectangle(cornerRadius: 22, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(accent.opacity(differentiateWithoutColor ? 0.9 : 0.28), lineWidth: differentiateWithoutColor ? 2 : 1)
        )
        .contentShape(Rectangle())
        .accessibilityElement(children: .combine)
        .accessibilityLabel(
            isActionable
                ? "Rescue cards. Immediate steps when a procedure is going wrong."
                : "\(title). \(subtitle)"
        )
        .accessibilitySortPriority(isActionable ? 1 : 0)
    }
}

struct PathwayTile: View {
    let pathway: ClinicalPathway
    let count: Int
    /// The chip must grow with the glyph, or the SF Symbol renders outside its
    /// tinted background at accessibility sizes and simply looks broken.
    @ScaledMetric(relativeTo: .title3) private var iconSize: CGFloat = 34

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Image(systemName: pathway.systemImage)
                .font(.title3.weight(.semibold))
                .foregroundStyle(pathway.tint)
                .frame(width: iconSize, height: iconSize)
                .background(pathway.tint.opacity(0.14), in: RoundedRectangle(cornerRadius: AppLayout.iconContainerRadius, style: .continuous))

            VStack(alignment: .leading, spacing: 2) {
                Text(pathway.title)
                    .font(.subheadline.weight(.semibold))
                    .foregroundStyle(.primary)
                    .fixedSize(horizontal: false, vertical: true)
                // The count was a capsule badge fighting the title for the
                // corner. It is quiet now, but it stays: these pathways hold
                // anywhere from 1 to 28 procedures, so the number is the
                // honest shape of the library rather than decoration.
                Text("\(count)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .frame(maxWidth: .infinity, minHeight: 92, alignment: .topLeading)
        .padding(14)
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous).stroke(.secondary.opacity(0.12), lineWidth: 1))
        .contentShape(Rectangle())
    }
}

struct ClinicalPathway: Identifiable, Hashable {
    let id: String
    let title: String
    let subtitle: String
    let systemImage: String
    let tint: Color
    let categories: [ProcedureCategory]

    static func == (lhs: ClinicalPathway, rhs: ClinicalPathway) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }

    static let defaultPathways: [ClinicalPathway] = [
        ClinicalPathway(id: "airway", title: "Airway", subtitle: "ETT, RSI, cric, failed airway", systemImage: "lungs.fill", tint: .cyan, categories: [.airway]),
        ClinicalPathway(id: "lines", title: "Lines", subtitle: "CVC, IJ, access, dialysis", systemImage: "drop.fill", tint: .blue, categories: [.vascularAccess, .ultrasoundGuided]),
        ClinicalPathway(id: "thoracic", title: "Thoracic", subtitle: "Chest tube, pigtail, needle", systemImage: "stethoscope", tint: .indigo, categories: [.thoracic]),
        // Green, not red. Red is reserved for the rescue signpost and appears
        // exactly once on this screen; a red tile sitting in the grid directly
        // beneath it spends the signal the signpost depends on. This costs the
        // familiar heart-is-red association, which is the right trade: the tile
        // is wayfinding, and urgency here belongs to one element only.
        ClinicalPathway(id: "resus", title: "Resus", subtitle: "Pacer, pericardiocentesis, crash", systemImage: "heart.fill", tint: .green, categories: [.cardiacResuscitation]),
        ClinicalPathway(id: "blocks", title: "Blocks", subtitle: "Digital and regional anesthesia", systemImage: "syringe", tint: .purple, categories: [.regionalAnesthesia]),
        ClinicalPathway(id: "neuro", title: "Neuro", subtitle: "LP, CSF, meningitis workup", systemImage: "brain.head.profile", tint: .orange, categories: [.neuro]),
        ClinicalPathway(id: "sedation", title: "Sedation", subtitle: "Procedural sedation and analgesia", systemImage: "moon.zzz.fill", tint: .teal, categories: [.sedationAnalgesia]),
        ClinicalPathway(id: "wound", title: "Wound & Soft Tissue", subtitle: "Abscess I&D, lacerations, wound care", systemImage: "bandage.fill", tint: .brown, categories: [.woundSoftTissue])
    ]
}

struct PathwayProcedureListView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    let pathway: ClinicalPathway

    private var procedures: [Procedure] {
        repository.procedures
            .filter { pathway.categories.contains($0.category) }
            .sorted { $0.title.localizedCaseInsensitiveCompare($1.title) == .orderedAscending }
    }

    var body: some View {
        List {
            Section {
                HStack(spacing: 12) {
                    Image(systemName: pathway.systemImage)
                        .font(.title2.weight(.semibold))
                        .foregroundStyle(pathway.tint)
                        .frame(width: 44, height: 44)
                        .background(pathway.tint.opacity(0.14), in: RoundedRectangle(cornerRadius: 12, style: .continuous))
                    VStack(alignment: .leading, spacing: 3) {
                        Text(pathway.title)
                            .font(.title3.weight(.bold))
                        // The count the tile no longer carries: here it has
                        // room to say what it means.
                        Text("\(procedures.count) procedure\(procedures.count == 1 ? "" : "s") · \(pathway.subtitle)")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                            .fixedSize(horizontal: false, vertical: true)
                    }
                }
                .padding(.vertical, 4)
                .accessibilityElement(children: .combine)
            }

            Section("Procedures") {
                if procedures.isEmpty {
                    // Only claim the emptiness is deliberate when the library
                    // actually loaded. This line used to be unconditional, so
                    // a failed decode produced an affirmative reassurance that
                    // nothing was wrong — on the one screen where the reader
                    // had just gone looking for the missing content.
                    if let error = repository.loadError {
                        Label {
                            VStack(alignment: .leading, spacing: 2) {
                                Text("Procedures unavailable").font(.subheadline.weight(.semibold))
                                Text(error).font(.footnote).foregroundStyle(.secondary)
                            }
                        } icon: {
                            Image(systemName: "exclamationmark.triangle.fill")
                        }
                        .foregroundStyle(AppSemanticColor.warningText)
                        .fixedSize(horizontal: false, vertical: true)
                        .accessibilityElement(children: .combine)
                    } else if repository.procedures.isEmpty {
                        Text("The procedure library is empty. This is not expected — reinstall the app or restore the bundled content.")
                            .font(.subheadline)
                            .foregroundStyle(AppSemanticColor.warningText)
                    } else {
                        Text("No procedures in this pathway yet. Content is added before release rather than showing empty categories.")
                            .font(.subheadline)
                            .foregroundStyle(.secondary)
                    }
                } else {
                    // This list already lives inside a pushed destination. Keep the
                    // next drill-down explicit so taps cannot be misrouted back to
                    // the pathway screen by stack-level route resolution.
                    ForEach(procedures) { procedure in
                        NavigationLink {
                            ProcedureDetailView(procedure: procedure)
                        } label: {
                            ProcedureCard(procedure: procedure, isFavorite: userData.isFavorite(procedure))
                        }
                    }
                }
            }
        }
        .navigationTitle(pathway.title)
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct AllRescueCardsListView: View {
    @EnvironmentObject private var repository: ProcedureRepository

    var body: some View {
        List {
            Section {
                Text("Problem-first cards for the moment a procedure starts going sideways.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }

            Section("Immediate Rescue") {
                // Same rule as the pathway list above: this view is already one
                // level deep, so the next hop stays explicit.
                ForEach(repository.rescueCards) { card in
                    NavigationLink {
                        RescueCardDetailView(card: card)
                    } label: {
                        RescueCardRow(card: card)
                    }
                }
            }
        }
        .navigationTitle("Rescue Cards")
    }
}

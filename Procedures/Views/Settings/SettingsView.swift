import SwiftUI

/// App-wide appearance preference. Stored as a raw string in AppStorage and
/// applied at the root via `.preferredColorScheme`.
enum AppAppearance: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var label: String {
        switch self {
        case .system: return "System"
        case .light: return "Light"
        case .dark: return "Dark"
        }
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system: return nil
        case .light: return .light
        case .dark: return .dark
        }
    }
}

enum SettingsStorageKey {
    static let appearance = "Procedures.appearance"
    static let defaultSection = "Procedures.defaultSection"
    static let disclaimerAccepted = "Procedures.hasAcceptedClinicalDisclaimer"
    static let hideGovernanceCopy = "Procedures.hideGovernanceCopy"
    static let reviewModeEnabled = "Procedures.reviewModeEnabled"
}

struct SettingsView: View {
    @EnvironmentObject private var repository: ProcedureRepository
    @EnvironmentObject private var userData: UserDataStore
    @Environment(\.dismiss) private var dismiss

    @AppStorage(SettingsStorageKey.appearance) private var appearanceRaw = AppAppearance.system.rawValue
    @AppStorage(SettingsStorageKey.defaultSection) private var defaultSectionRaw = ProcedureDetailSection.shiftMode.rawValue
    @AppStorage(SettingsStorageKey.disclaimerAccepted) private var hasAcceptedDisclaimer = false
    @AppStorage(SettingsStorageKey.hideGovernanceCopy) private var hideGovernanceCopy = true
    @AppStorage(SettingsStorageKey.reviewModeEnabled) private var reviewModeEnabled = false

    @State private var confirmation: DataAction?

    private var appearance: Binding<AppAppearance> {
        Binding(
            get: { AppAppearance(rawValue: appearanceRaw) ?? .system },
            set: { appearanceRaw = $0.rawValue }
        )
    }

    private var defaultSection: Binding<ProcedureDetailSection> {
        Binding(
            get: { ProcedureDetailSection(rawValue: defaultSectionRaw) ?? .shiftMode },
            set: { defaultSectionRaw = $0.rawValue }
        )
    }

    var body: some View {
        NavigationStack {
            Form {
                Section("Appearance") {
                    Picker("Theme", selection: appearance) {
                        ForEach(AppAppearance.allCases) { option in
                            Text(option.label).tag(option)
                        }
                    }
                }

                Section {
                    Picker("Open procedures to", selection: defaultSection) {
                        ForEach(ProcedureDetailSection.allCases) { section in
                            Text(section.rawValue).tag(section)
                        }
                    }
                    Toggle("Clinical Mode", isOn: $hideGovernanceCopy)
                } header: {
                    Text("Procedure Pages")
                } footer: {
                    Text("Clinical Mode keeps bedside screens quiet by hiding governance copy, disclaimers, source review badges, and visual warning callouts. Procedure clinical content remains visible.")
                }

                Section {
                    Toggle("Show Review Center Tab", isOn: $reviewModeEnabled)
                    NavigationLink {
                        ReviewCenterView()
                    } label: {
                        Label("Open Review Center", systemImage: "checkmark.seal")
                    }
                } header: {
                    Text("Review Mode")
                } footer: {
                    Text("Review Center is the editor workspace for content review, issue fixing, and local reviewer notes. Keep it off for the clean bedside app.")
                }

                Section {
                    Button(role: .destructive) { confirmation = .clearRecents } label: {
                        Label("Clear Recently Viewed", systemImage: "clock.arrow.circlepath")
                    }
                    Button(role: .destructive) { confirmation = .clearFavorites } label: {
                        Label("Clear Saved Procedures", systemImage: "bookmark.slash")
                    }
                    Button(role: .destructive) { confirmation = .clearChecklists } label: {
                        Label("Reset Equipment Checklists", systemImage: "checklist.unchecked")
                    }
                    Button(role: .destructive) { confirmation = .clearKitChecklists } label: {
                        Label("Reset Kit Room-Setup Checklists", systemImage: "shippingbox")
                    }
                    Button(role: .destructive) { confirmation = .clearNotes } label: {
                        Label("Delete Local Notes", systemImage: "trash")
                    }
                    Button(role: .destructive) { confirmation = .clearReviews } label: {
                        Label("Clear My Review Marks", systemImage: "checkmark.seal")
                    }
                } header: {
                    Text("My Data")
                } footer: {
                    Text("Favorites, recents, checklists, notes, and review marks are stored only on this device.")
                }

                Section {
                    if hideGovernanceCopy {
                        Label("Governance copy is hidden", systemImage: "eye.slash")
                    } else {
                        Button {
                            hasAcceptedDisclaimer = false
                            dismiss()
                        } label: {
                            Label("Show Disclaimer Again", systemImage: "exclamationmark.shield")
                        }
                    }
                } header: {
                    Text("About")
                } footer: {
                    if !hideGovernanceCopy {
                        Text(AppConstants.clinicalDisclaimer)
                    }
                }

                Section("App") {
                    LabeledContent("Version", value: AppConstants.appVersionDescription)
                }
            }
            .navigationTitle("Settings")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Done") { dismiss() }
                }
            }
            .navigationDestination(for: Procedure.self) { procedure in
                ProcedureDetailView(procedure: procedure)
            }
            .navigationDestination(for: ComplicationRescueCard.self) { card in
                RescueCardDetailView(card: card)
            }
            .navigationDestination(for: Kit.self) { kit in
                KitDetailView(kit: kit)
            }
            .confirmationDialog(
                confirmation?.title ?? "",
                isPresented: Binding(
                    get: { confirmation != nil },
                    set: { if !$0 { confirmation = nil } }
                ),
                titleVisibility: .visible
            ) {
                if let action = confirmation {
                    Button(action.confirmLabel, role: .destructive) {
                        perform(action)
                    }
                }
            }
        }
    }

    private func perform(_ action: DataAction) {
        switch action {
        case .clearRecents: userData.clearRecents()
        case .clearFavorites: userData.clearFavorites()
        case .clearChecklists: userData.clearAllEquipment()
        case .clearKitChecklists: userData.clearAllKitChecklists()
        case .clearNotes: userData.clearAllNotes()
        case .clearReviews: userData.clearAllLocalReviews()
        }
        confirmation = nil
    }
}

private enum DataAction: Identifiable {
    case clearRecents
    case clearFavorites
    case clearChecklists
    case clearKitChecklists
    case clearNotes
    case clearReviews

    var id: String { title }

    var title: String {
        switch self {
        case .clearRecents: return "Clear all recently viewed procedures?"
        case .clearFavorites: return "Remove all saved procedures?"
        case .clearChecklists: return "Reset every equipment checklist?"
        case .clearKitChecklists: return "Reset every kit room-setup checklist?"
        case .clearNotes: return "Delete all local notes?"
        case .clearReviews: return "Clear every local review mark?"
        }
    }

    var confirmLabel: String {
        switch self {
        case .clearRecents: return "Clear Recents"
        case .clearFavorites: return "Clear Saved"
        case .clearChecklists: return "Reset Checklists"
        case .clearKitChecklists: return "Reset Kit Checklists"
        case .clearNotes: return "Delete Notes"
        case .clearReviews: return "Clear Reviews"
        }
    }
}

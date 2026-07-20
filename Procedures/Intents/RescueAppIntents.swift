import AppIntents

/// Opens the Rescue tab, which lists Crash-acuity cards first. Exposed to
/// Siri, Spotlight, the Shortcuts app, and the lock-screen Action button, so
/// a gloved clinician can reach crash content by voice or one press without
/// navigating the app.
struct OpenRescueIntent: AppIntent {
    static let title: LocalizedStringResource = "Open Rescue Cards"
    static let description = IntentDescription(
        "Opens the rescue cards with Crash-acuity problems listed first."
    )
    static let openAppWhenRun = true

    @MainActor
    func perform() async throws -> some IntentResult {
        DeepLinkRouter.shared.destination = .rescueTab
        return .result()
    }
}

struct ProceduresAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: OpenRescueIntent(),
            phrases: [
                "Open rescue in \(.applicationName)",
                "Show rescue cards in \(.applicationName)",
                "\(.applicationName) rescue"
            ],
            shortTitle: "Rescue",
            systemImageName: "lifepreserver.fill"
        )
    }
}

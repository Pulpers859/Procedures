import Foundation
import Combine

/// Routes external entry points (Core Spotlight results, App Intents / Siri)
/// to in-app destinations. External activations arrive before or after the
/// relevant view exists, so the pending destination is held here and consumed
/// by whichever view can satisfy it.
@MainActor
final class DeepLinkRouter: ObservableObject {
    enum Destination: Equatable {
        case rescueTab
        case rescueCard(id: String)
        case procedure(id: String)
    }

    static let shared = DeepLinkRouter()

    @Published var destination: Destination?

    private init() {}

    /// Spotlight unique identifiers are "<kind>:<content id>"; see
    /// SpotlightIndexer. Unknown identifiers fall back to the rescue tab —
    /// for a bedside tool, landing near crash content beats landing nowhere.
    func openSpotlightItem(identifier: String) {
        let parts = identifier.split(separator: ":", maxSplits: 1).map(String.init)
        guard parts.count == 2 else {
            destination = .rescueTab
            return
        }
        switch parts[0] {
        case SpotlightIndexer.rescueKind:
            destination = .rescueCard(id: parts[1])
        case SpotlightIndexer.procedureKind:
            destination = .procedure(id: parts[1])
        default:
            destination = .rescueTab
        }
    }
}

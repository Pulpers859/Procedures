import Foundation
import CoreSpotlight
import UniformTypeIdentifiers

/// Publishes procedures and rescue cards to Core Spotlight so the crash path
/// starts at the lock screen: swipe, type "last", tap — no app navigation.
/// The index is rebuilt from shipped content on every launch; content JSON is
/// the single source of truth and the index is always disposable.
enum SpotlightIndexer {
    static let procedureKind = "procedure"
    static let rescueKind = "rescue"
    private static let domainIdentifier = "com.procedures.content"

    static func reindex(procedures: [Procedure], rescueCards: [ComplicationRescueCard]) {
        guard CSSearchableIndex.isIndexingAvailable() else { return }

        var items: [CSSearchableItem] = []
        items.reserveCapacity(procedures.count + rescueCards.count)

        for card in rescueCards {
            let attributes = CSSearchableItemAttributeSet(contentType: .text)
            attributes.title = card.title
            attributes.contentDescription = card.trigger.first ?? "Rescue card"
            attributes.keywords = card.tags + [card.acuity.rawValue.lowercased(), "rescue"]
            items.append(CSSearchableItem(
                uniqueIdentifier: "\(rescueKind):\(card.id)",
                domainIdentifier: domainIdentifier,
                attributeSet: attributes
            ))
        }

        for procedure in procedures {
            let attributes = CSSearchableItemAttributeSet(contentType: .text)
            attributes.title = procedure.title
            attributes.contentDescription = procedure.category.rawValue
            attributes.keywords = procedure.tags + [procedure.category.rawValue.lowercased()]
            items.append(CSSearchableItem(
                uniqueIdentifier: "\(procedureKind):\(procedure.id)",
                domainIdentifier: domainIdentifier,
                attributeSet: attributes
            ))
        }

        let index = CSSearchableIndex.default()
        index.deleteSearchableItems(withDomainIdentifiers: [domainIdentifier]) { _ in
            // A failed delete only risks stale duplicates; still index fresh
            // content. Indexing failure is non-fatal: in-app search is the
            // primary path and remains fully functional.
            index.indexSearchableItems(items, completionHandler: nil)
        }
    }
}

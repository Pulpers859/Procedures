import Foundation

/// Editorial review state for a piece of clinical content. This is a safety
/// surface, not decoration: the app must never imply that draft or unreviewed
/// material has been clinically approved. When content omits the field we fall
/// back to the most conservative honest answer (`needsClinicalReview`) rather
/// than assuming the best.
enum ReviewerStatus: String, Codable, Hashable, CaseIterable {
    case draft = "Draft"
    case needsClinicalReview = "Needs Clinical Review"
    case internallyReviewed = "Internally Reviewed"
    case externallyReviewed = "Externally Reviewed"
    case institutionSpecific = "Institution-Specific"

    /// Applied when content does not declare a status. Deliberately pessimistic.
    static let unreviewedDefault: ReviewerStatus = .needsClinicalReview

    /// True only once a clinician has signed off. Draft and needs-review content
    /// must be presented to the user with an explicit "not yet reviewed" caveat.
    var isClinicallyReviewed: Bool {
        switch self {
        case .draft, .needsClinicalReview:
            return false
        case .internallyReviewed, .externallyReviewed, .institutionSpecific:
            return true
        }
    }

    /// SF Symbol used to badge the status in governance UI.
    var systemImage: String {
        switch self {
        case .draft: return "pencil.and.outline"
        case .needsClinicalReview: return "exclamationmark.triangle.fill"
        case .internallyReviewed: return "checkmark.seal"
        case .externallyReviewed: return "checkmark.seal.fill"
        case .institutionSpecific: return "building.2.fill"
        }
    }

    /// One-line plain-language explanation for the governance panel.
    var explanation: String {
        switch self {
        case .draft:
            return "Drafted but not yet submitted for clinical review. Do not treat as authoritative."
        case .needsClinicalReview:
            return "Awaiting formal clinical review. Verify against a trusted source before bedside use."
        case .internallyReviewed:
            return "Reviewed internally by the content team. Not yet externally validated."
        case .externallyReviewed:
            return "Reviewed by an external clinical expert. Still subject to local policy."
        case .institutionSpecific:
            return "Adapted to a specific institution's policy. May not apply elsewhere."
        }
    }
}

/// Provenance of a content item: who produced the words the clinician is
/// reading. Orthogonal to `ReviewerStatus` (review state): an AI draft stays
/// `ai-draft` until a human takes editorial ownership, and a clinician
/// sign-off must update this field — the validators treat a "clinically
/// reviewed" status on an `ai-draft` item as a contradiction.
enum ContentSource: String, Codable, Hashable, CaseIterable {
    case aiDraft = "ai-draft"
    case humanAuthored = "human-authored"
    case clinicianReviewed = "clinician-reviewed"

    /// Applied when content does not declare a source. Deliberately the least
    /// trusted answer: undeclared provenance is treated as an AI draft.
    static let undeclaredDefault: ContentSource = .aiDraft

    /// Plain-language label for governance UI.
    var displayLabel: String {
        switch self {
        case .aiDraft: return "AI draft — not clinically reviewed"
        case .humanAuthored: return "Human-authored"
        case .clinicianReviewed: return "Clinician-reviewed"
        }
    }
}

/// Last-reviewed aging logic, shared by the in-app validator and governance UI.
/// Mirrors the Python validator so a single staleness threshold governs both.
enum ContentFreshness {
    /// Content older than this is flagged as stale and due for re-review.
    static let stalenessThresholdDays = 365

    private static let formatter: DateFormatter = {
        let formatter = DateFormatter()
        formatter.calendar = Calendar(identifier: .iso8601)
        formatter.locale = Locale(identifier: "en_US_POSIX")
        formatter.timeZone = TimeZone(identifier: "UTC")
        formatter.dateFormat = "yyyy-MM-dd"
        return formatter
    }()

    /// Days elapsed since the supplied ISO `yyyy-MM-dd` date, or `nil` if the
    /// string cannot be parsed (an unparseable date is its own content issue).
    static func daysSinceReview(_ lastReviewed: String, now: Date = Date()) -> Int? {
        let trimmed = lastReviewed.trimmingCharacters(in: .whitespacesAndNewlines)
        guard let date = formatter.date(from: trimmed) else { return nil }
        return Calendar(identifier: .iso8601).dateComponents([.day], from: date, to: now).day
    }

    /// True when content is past the staleness threshold. Unparseable dates are
    /// not reported here; they surface as a separate metadata blocker.
    static func isStale(_ lastReviewed: String, now: Date = Date()) -> Bool {
        guard let days = daysSinceReview(lastReviewed, now: now) else { return false }
        return days > stalenessThresholdDays
    }

    /// True when `lastReviewed` is present but not a valid ISO date.
    static func isUnparseableDate(_ lastReviewed: String) -> Bool {
        let trimmed = lastReviewed.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return false }
        return formatter.date(from: trimmed) == nil
    }
}

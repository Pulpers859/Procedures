import Foundation
import CryptoKit

/// Stable fingerprint of the *clinically material* part of a content item.
///
/// A review belongs to the clinician who made it and does not expire because
/// the app updated: fixing a typo, adding a tag, or reformatting a reference
/// must never cost someone their sign-off. But if the steps, the doses, the
/// contraindications, or the complications change, a prior "Reviewed" is
/// vouching for words that were never read — so those, and only those, are
/// fingerprinted here.
///
/// Swift's `Hasher` is seeded per process, so `hashValue` cannot be persisted
/// and compared across launches. SHA-256 is stable forever, which is what a
/// stored review baseline requires.
enum ContentFingerprint {
    /// Unit separator — a character that cannot appear in clinical prose, so
    /// ["ab", "c"] and ["a", "bc"] cannot collide.
    private static let separator = "\u{1F}"

    /// Record separator, marking where one section ends and the next begins.
    ///
    /// The unit separator solves collisions *within* a list but not *between*
    /// them: concatenating steps + complications meant a line moving from the
    /// end of one to the start of the other produced a byte-identical digest.
    /// Kits were the likeliest case — moving an item from "in the kit" to
    /// "outside the kit" is a meaningful correction that changed nothing.
    private static let sectionSeparator = "\u{1E}"

    /// Incremented whenever the *set* of fields hashed changes.
    ///
    /// Records written under an older version cannot be compared against a
    /// newer digest — the two answer different questions. Without this, adding
    /// a section would have flipped every existing sign-off to "Review out of
    /// date" and told the reader their content had changed when nothing had.
    /// A version mismatch reads as `.unknownBaseline` instead, which is the
    /// truth: no comparison is possible, and nothing is reported.
    ///
    /// v5: added `majorBlockMonitoring` - a procedure-level flag replacing a
    /// checklist line that used to live directly in `equipment` prose for 14
    /// regional blocks. It is still material (it is a monitoring
    /// requirement, not editorial metadata), so it must still revoke a stale
    /// sign-off if it changes.
    ///
    /// v6: added `seniorPearls`, now the single home for clinical rationale
    /// rather than assorted tips. Reasoning that drives a step is material.
    static let version = 6

    static func make(_ parts: [String]) -> String {
        let joined = parts.joined(separator: separator)
        let digest = SHA256.hash(data: Data(joined.utf8))
        return digest.map { String(format: "%02x", $0) }.joined()
    }

    /// Fingerprints named sections, keeping their boundaries significant.
    static func make(sections: [(name: String, lines: [String])]) -> String {
        var parts: [String] = []
        for section in sections {
            parts.append(sectionSeparator + section.name)
            parts.append(contentsOf: section.lines)
        }
        return make(parts)
    }
}

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

    /// Compact form for the collapsed provenance summary. Says the same thing
    /// as `displayLabel` without the clause that only fits on its own row.
    var shortLabel: String {
        switch self {
        case .aiDraft: return "AI draft"
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

    /// Today as an ISO `yyyy-MM-dd` string, in the one format this app stamps
    /// dates with.
    ///
    /// The local stores each carried a byte-identical private copy of the
    /// formatter above and their own `todayString`. Three independent
    /// definitions of one format is three places to edit and two chances to
    /// miss: a change to any one of them would desync the dates the stores
    /// write from the dates this type parses, with nothing to catch it.
    static func todayString(now: Date = Date()) -> String {
        formatter.string(from: now)
    }
}

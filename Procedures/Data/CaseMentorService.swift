import Foundation
#if canImport(FoundationNetworking)
import FoundationNetworking
#endif

enum CaseMentorServiceError: LocalizedError {
    case missingAPIKey
    case invalidURL
    case invalidResponse
    case apiError(String)
    case emptyResponse

    var errorDescription: String? {
        switch self {
        case .missingAPIKey:
            return "Add an OpenAI API key in Settings before running an AI mentor review."
        case .invalidURL:
            return "The mentor review endpoint URL is invalid."
        case .invalidResponse:
            return "The mentor review service returned an unreadable response."
        case .apiError(let message):
            return message
        case .emptyResponse:
            return "The mentor review came back empty."
        }
    }
}

enum CaseMentorDefaults {
    static let model = "gpt-5.6-sol"
}

struct OpenAIResponsesMentorService {
    private let session: URLSession

    init(session: URLSession = .shared) {
        self.session = session
    }

    func review(
        caseReview: CriticalCaseReview,
        privacyFindings: [CasePrivacyFinding],
        apiKey: String,
        model: String
    ) async throws -> CaseMentorFeedback {
        let trimmedKey = apiKey.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedKey.isEmpty else {
            throw CaseMentorServiceError.missingAPIKey
        }
        guard let url = URL(string: "https://api.openai.com/v1/responses") else {
            throw CaseMentorServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("Bearer \(trimmedKey)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body = OpenAIResponseRequest(
            model: model.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? CaseMentorDefaults.model : model,
            instructions: ClinicalCaseMentorPrompt.instructions,
            input: ClinicalCaseMentorPrompt.input(
                for: caseReview,
                privacyFindings: privacyFindings
            ),
            store: false
        )
        request.httpBody = try JSONEncoder().encode(body)

        let (data, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw CaseMentorServiceError.invalidResponse
        }

        if !(200..<300).contains(httpResponse.statusCode) {
            if let decoded = try? JSONDecoder().decode(OpenAIErrorEnvelope.self, from: data) {
                throw CaseMentorServiceError.apiError(decoded.error.message)
            }
            throw CaseMentorServiceError.apiError("Mentor review failed with HTTP \(httpResponse.statusCode).")
        }

        let decoded = try JSONDecoder().decode(OpenAIResponseEnvelope.self, from: data)
        let content = decoded.outputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !content.isEmpty else {
            throw CaseMentorServiceError.emptyResponse
        }

        return CaseMentorFeedback(
            model: body.model,
            content: content,
            privacyFindings: privacyFindings
        )
    }
}

private struct OpenAIResponseRequest: Encodable {
    let model: String
    let instructions: String
    let input: String
    let store: Bool
}

private struct OpenAIResponseEnvelope: Decodable {
    struct OutputItem: Decodable {
        struct ContentItem: Decodable {
            let type: String
            let text: String?
        }

        let type: String
        let content: [ContentItem]?
    }

    let output: [OutputItem]

    var outputText: String {
        output
            .flatMap { $0.content ?? [] }
            .filter { $0.type == "output_text" }
            .compactMap(\.text)
            .joined(separator: "\n\n")
    }
}

private struct OpenAIErrorEnvelope: Decodable {
    struct APIError: Decodable {
        let message: String
    }

    let error: APIError
}

enum ClinicalCaseMentorPrompt {
    static let instructions = """
    You are a long-time emergency medicine and critical care mentor reviewing a de-identified case for a clinician's private learning.

    Your job is to improve the clinician's judgment, pattern recognition, resuscitation priorities, and management under pressure. Be direct, specific, and constructive. Do not flatter. Do not reassure without evidence. Do not produce generic AI summaries.

    Identify missed risks, weak reasoning, premature closure, delayed reassessment, delayed escalation, high-risk disposition choices, and alternative management paths. Separate must-know safety issues from judgment calls, local-practice variation, and details that cannot be judged from the provided case.

    If the case is missing key details, say exactly what information would change your assessment. Do not invent data. Do not give patient-facing advice. Do not quote or preserve any identifier-like detail if one appears in the note.

    Use these headings exactly:
    Bottom Line
    What Was Solid
    Where Your Reasoning Was Vulnerable
    What I Wanted Earlier
    Alternative Management Paths
    Dangerous Misses
    Next-Shift Drill
    """

    static func input(
        for caseReview: CriticalCaseReview,
        privacyFindings: [CasePrivacyFinding]
    ) -> String {
        let privacyLine: String
        if privacyFindings.isEmpty {
            privacyLine = "Privacy Guard findings: none supplied."
        } else {
            privacyLine = "Privacy Guard findings: \(privacyFindings.map { $0.kind.rawValue }.joined(separator: ", ")). Do not repeat identifier-like details."
        }

        return """
        Case title: \(caseReview.displayTitle)
        Template: \(caseReview.template.rawValue)
        Mentor lens: \(caseReview.lens.rawValue)
        Review depth: \(caseReview.depth.rawValue)
        Depth instruction: \(caseReview.depth.promptDirection)
        \(privacyLine)

        De-identified case narrative:
        \(caseReview.caseText)
        """
    }
}

enum CasePrivacyScanner {
    static func findings(in text: String) -> [CasePrivacyFinding] {
        var findings: [CasePrivacyFinding] = []
        findings.append(contentsOf: matches(
            in: text,
            pattern: #"(?i)\b(?:mrn|medical record|account)\s*[:#-]?\s*[A-Z0-9-]{5,}\b"#,
            kind: .medicalRecordNumber,
            suggestion: "Replace chart identifiers with broad clinical context."
        ))
        findings.append(contentsOf: matches(
            in: text,
            pattern: #"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{1,2}-\d{1,2})\b"#,
            kind: .exactDate,
            suggestion: "Use a broad interval instead of an exact date."
        ))
        findings.append(contentsOf: matches(
            in: text,
            pattern: #"\b\d{1,2}:\d{2}\s?(?:AM|PM|am|pm)?\b"#,
            kind: .timestamp,
            suggestion: "Use a broad sequence such as early course, later reassessment, or after signout."
        ))
        findings.append(contentsOf: matches(
            in: text,
            pattern: #"\b(?:9[0-9]|1[0-2][0-9])\s?(?:yo|y/o|year old|years old)\b"#,
            kind: .ageOver89,
            suggestion: "Use age over 89 or a broad age band."
        ))
        findings.append(contentsOf: matches(
            in: text,
            pattern: #"\b(?:[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4})\b"#,
            kind: .contact,
            suggestion: "Remove contact details."
        ))

        return Array(findings.prefix(8))
    }

    private static func matches(
        in text: String,
        pattern: String,
        kind: CasePrivacyFinding.Kind,
        suggestion: String
    ) -> [CasePrivacyFinding] {
        guard let regex = try? NSRegularExpression(pattern: pattern) else { return [] }
        let range = NSRange(text.startIndex..<text.endIndex, in: text)
        return regex.matches(in: text, range: range).compactMap { match in
            guard let matchRange = Range(match.range, in: text) else { return nil }
            return CasePrivacyFinding(
                kind: kind,
                excerpt: String(text[matchRange]),
                suggestion: suggestion
            )
        }
    }
}

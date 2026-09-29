import SwiftUI
import UIKit

extension Procedure {
    var hasVisualAssets: Bool {
        guard let assets = visualAssets else { return false }
        return !assets.isEmpty
    }
}

enum ProcedureVisualLoader {
    static func image(for asset: ProcedureVisualAsset) -> UIImage? {
        guard let assetName = asset.assetName, !assetName.isEmpty else { return nil }

        for name in [assetName, "Visuals/\(assetName)"] {
            if let image = UIImage(named: name) {
                return image
            }
        }

        let name = (assetName as NSString).deletingPathExtension
        let ext = (assetName as NSString).pathExtension
        let extensions = ext.isEmpty ? [nil, "png", "jpg", "jpeg"] : [ext]
        let subdirectories: [String?] = [nil, "Visuals"]

        for subdirectory in subdirectories {
            for itemExtension in extensions {
                if let url = Bundle.main.url(forResource: ext.isEmpty ? assetName : name, withExtension: itemExtension, subdirectory: subdirectory),
                   let image = UIImage(contentsOfFile: url.path) {
                    return image
                }
            }
        }

        return nil
    }
}

/// Images the reader adds to a visual slot on the device — an ultrasound still
/// or a rhythm strip, where a drawing would teach the wrong thing. They live
/// only on this phone, under Application Support, keyed by the visual asset id.
/// Bundled artwork always wins: an import only fills a slot that has none.
enum ImportedVisualStore {
    /// Long edge after import. Enough for a card and zoom, small on disk.
    private static let maxPixelLength: CGFloat = 2400

    static var directory: URL {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask).first
            ?? FileManager.default.temporaryDirectory
        return base.appendingPathComponent("ImportedVisuals", isDirectory: true)
    }

    static func fileURL(for assetID: String) -> URL {
        let safe = assetID.unicodeScalars
            .map { CharacterSet.alphanumerics.contains($0) || $0 == "_" || $0 == "-" ? String($0) : "_" }
            .joined()
        return directory.appendingPathComponent("\(safe).jpg")
    }

    static func image(for assetID: String) -> UIImage? {
        UIImage(contentsOfFile: fileURL(for: assetID).path)
    }

    /// Re-encodes as JPEG, which also drops the source file's metadata.
    @discardableResult
    static func save(_ data: Data, for assetID: String) throws -> UIImage {
        guard let source = UIImage(data: data) else { throw ImportError.unreadable }
        let image = downscaled(source)
        guard let jpeg = image.jpegData(compressionQuality: 0.9) else { throw ImportError.unreadable }
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        try jpeg.write(to: fileURL(for: assetID), options: [.atomic, .completeFileProtection])
        return image
    }

    static func remove(for assetID: String) {
        try? FileManager.default.removeItem(at: fileURL(for: assetID))
    }

    private static func downscaled(_ image: UIImage) -> UIImage {
        let longest = max(image.size.width, image.size.height) * image.scale
        let factor = longest > maxPixelLength ? maxPixelLength / longest : 1
        let size = CGSize(width: image.size.width * image.scale * factor, height: image.size.height * image.scale * factor)
        let format = UIGraphicsImageRendererFormat()
        format.scale = 1
        return UIGraphicsImageRenderer(size: size, format: format).image { _ in
            image.draw(in: CGRect(origin: .zero, size: size))
        }
    }

    enum ImportError: LocalizedError {
        case unreadable
        var errorDescription: String? { "That file is not an image this device can read." }
    }
}

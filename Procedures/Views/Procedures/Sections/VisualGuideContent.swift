import PhotosUI
import SwiftUI
import UIKit
import UniformTypeIdentifiers

struct VisualGuideContent: View {
    let procedure: Procedure

    private var assets: [ProcedureVisualAsset] {
        procedure.visualAssets ?? []
    }

    var body: some View {
        if assets.isEmpty {
            SectionCard(title: "Visual Guide", systemImage: "photo.on.rectangle.angled") {
                Text("No visual guides for this procedure yet.")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
            }
        } else {
            VStack(alignment: .leading, spacing: AppLayout.sectionSpacing) {
                ForEach(assets) { asset in
                    VisualAssetCard(asset: asset)
                }
            }
        }
    }
}

struct VisualAssetCard: View {
    let asset: ProcedureVisualAsset

    @State private var importedImage: UIImage?
    @State private var photoSelection: PhotosPickerItem?
    @State private var showingPhotoPicker = false
    @State private var showingFileImporter = false
    @State private var confirmingRemoval = false
    @State private var importError: String?
    @State private var fullScreenImage: FullScreenVisual?

    private var bundledImage: UIImage? { ProcedureVisualLoader.image(for: asset) }

    private var kindTint: Color {
        switch asset.kind {
        case .landmark: return .blue
        case .probePosition: return .cyan
        case .dangerZone: return .red
        case .confirmation: return .green
        case .setup: return .purple
        }
    }

    private var kindIcon: String {
        switch asset.kind {
        case .landmark: return "mappin.and.ellipse"
        case .probePosition: return "dot.viewfinder"
        case .dangerZone: return "exclamationmark.triangle.fill"
        case .confirmation: return "checkmark.seal.fill"
        case .setup: return "tray.2.fill"
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Kind badge header
            HStack(spacing: 8) {
                Image(systemName: kindIcon)
                    .font(.caption.weight(.bold))
                    .foregroundStyle(kindTint)
                Text(asset.kind.rawValue.uppercased())
                    .font(.caption2.weight(.heavy))
                    .foregroundStyle(kindTint)
                Spacer()
            }
            .padding(.horizontal, 16)
            .padding(.top, 14)
            .padding(.bottom, 10)

            // Bundled artwork, else an image imported on this device, else a
            // placeholder that offers the import.
            if let image = bundledImage {
                visualImage(image)
            } else if let image = importedImage {
                visualImage(image)
                HStack(spacing: 6) {
                    Label("Imported image", systemImage: "iphone")
                        .font(.caption2.weight(.semibold))
                        .foregroundStyle(.secondary)
                    Spacer()
                    Menu {
                        importButtons(replacing: true)
                        Button("Remove Image", systemImage: "trash", role: .destructive) {
                            confirmingRemoval = true
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                            .font(.body)
                            .frame(minWidth: 44, minHeight: 32)
                    }
                    .accessibilityLabel("Imported image options")
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 8)
            } else {
                SchematicPlaceholder(asset: asset, tint: kindTint) {
                    Menu {
                        importButtons(replacing: false)
                    } label: {
                        Label("Add Image", systemImage: "plus.circle.fill")
                            .font(.subheadline.weight(.semibold))
                            .frame(minHeight: 44)
                    }
                    .accessibilityLabel("Add an image for \(asset.displayName)")
                }
                .padding(.horizontal, 16)
                .padding(.bottom, 12)
            }

            // Title + subtitle
            VStack(alignment: .leading, spacing: 4) {
                if !asset.title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
                    Text(asset.title)
                        .font(.subheadline.weight(.semibold))
                }
                Text(asset.subtitle)
                    .font(.caption)
                    .foregroundStyle(.secondary)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .padding(.horizontal, 16)

            // Clinical warning
            if let warning = asset.clinicalWarning, !warning.isEmpty {
                HStack(alignment: .top, spacing: 8) {
                    Image(systemName: "exclamationmark.triangle.fill")
                        .font(.caption)
                        .foregroundStyle(AppSemanticColor.warningText)
                    Text(warning)
                        .font(.caption)
                        .foregroundStyle(AppSemanticColor.warningText)
                        .fixedSize(horizontal: false, vertical: true)
                }
                .padding(.horizontal, 16)
                .padding(.top, 8)
            }

            // Caption
            if !asset.caption.isEmpty {
                Text(asset.caption)
                    .font(.caption2)
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 16)
                    .padding(.top, 6)
            }

            Spacer().frame(height: 14)
        }
        .background(Color(.secondarySystemGroupedBackground), in: RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: AppLayout.cardRadius, style: .continuous)
                .stroke(kindTint.opacity(0.25), lineWidth: 1)
        )
        .task(id: asset.id) {
            if bundledImage == nil {
                importedImage = ImportedVisualStore.image(for: asset.id)
            }
        }
        .photosPicker(isPresented: $showingPhotoPicker, selection: $photoSelection, matching: .images)
        .onChange(of: photoSelection) { _, item in
            guard let item else { return }
            Task {
                defer { photoSelection = nil }
                do {
                    guard let data = try await item.loadTransferable(type: Data.self) else {
                        throw ImportedVisualStore.ImportError.unreadable
                    }
                    importedImage = try ImportedVisualStore.save(data, for: asset.id)
                } catch {
                    importError = error.localizedDescription
                }
            }
        }
        .fileImporter(isPresented: $showingFileImporter, allowedContentTypes: [.image], allowsMultipleSelection: false) { result in
            switch result {
            case .success(let urls):
                guard let url = urls.first else { return }
                let scoped = url.startAccessingSecurityScopedResource()
                defer { if scoped { url.stopAccessingSecurityScopedResource() } }
                do {
                    importedImage = try ImportedVisualStore.save(try Data(contentsOf: url), for: asset.id)
                } catch {
                    importError = error.localizedDescription
                }
            case .failure(let error):
                importError = error.localizedDescription
            }
        }
        .confirmationDialog("Remove this image?", isPresented: $confirmingRemoval, titleVisibility: .visible) {
            Button("Remove Image", role: .destructive) {
                ImportedVisualStore.remove(for: asset.id)
                importedImage = nil
            }
            Button("Cancel", role: .cancel) {}
        } message: {
            Text("It is stored only on this device and cannot be recovered.")
        }
        .alert("Could Not Import Image", isPresented: Binding(get: { importError != nil }, set: { if !$0 { importError = nil } })) {
            Button("OK", role: .cancel) { importError = nil }
        } message: {
            Text(importError ?? "")
        }
        .fullScreenCover(item: $fullScreenImage) { visual in
            ZoomableVisualView(image: visual.image, title: asset.displayName)
        }
    }

    private func visualImage(_ image: UIImage) -> some View {
        Button {
            fullScreenImage = FullScreenVisual(image: image)
        } label: {
            Image(uiImage: image)
                .resizable()
                .scaledToFit()
                .frame(maxWidth: .infinity)
                .clipShape(RoundedRectangle(cornerRadius: AppLayout.mediaRadius, style: .continuous))
        }
        .buttonStyle(.plain)
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
        .accessibilityLabel(asset.displayName)
        .accessibilityHint("Opens full screen with zoom")
    }

    @ViewBuilder
    private func importButtons(replacing: Bool) -> some View {
        Button(replacing ? "Replace from Photos" : "From Photos", systemImage: "photo.on.rectangle") {
            showingPhotoPicker = true
        }
        Button(replacing ? "Replace from Files" : "From Files", systemImage: "folder") {
            showingFileImporter = true
        }
    }
}

private struct FullScreenVisual: Identifiable {
    let id = UUID()
    let image: UIImage
}

/// Full-screen view for a visual: pinch to zoom, drag to pan while zoomed,
/// double-tap to toggle between fit and 2.5x.
struct ZoomableVisualView: View {
    let image: UIImage
    let title: String

    @Environment(\.dismiss) private var dismiss
    @State private var scale: CGFloat = 1
    @State private var baseScale: CGFloat = 1
    @State private var offset: CGSize = .zero
    @State private var baseOffset: CGSize = .zero

    var body: some View {
        NavigationStack {
            GeometryReader { _ in
                Image(uiImage: image)
                    .resizable()
                    .scaledToFit()
                    .scaleEffect(scale)
                    .offset(offset)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .contentShape(Rectangle())
                    .gesture(
                        MagnifyGesture()
                            .onChanged { value in scale = min(max(baseScale * value.magnification, 1), 6) }
                            .onEnded { _ in
                                baseScale = scale
                                if scale == 1 { resetPan() }
                            }
                            .simultaneously(with: DragGesture()
                                .onChanged { value in
                                    guard scale > 1 else { return }
                                    offset = CGSize(width: baseOffset.width + value.translation.width,
                                                    height: baseOffset.height + value.translation.height)
                                }
                                .onEnded { _ in baseOffset = offset })
                    )
                    .onTapGesture(count: 2) {
                        withAnimation(.snappy) {
                            if scale > 1 {
                                scale = 1
                                baseScale = 1
                                resetPan()
                            } else {
                                scale = 2.5
                                baseScale = 2.5
                            }
                        }
                    }
            }
            .background(Color.black)
            .navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbarBackground(.visible, for: .navigationBar)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Done") { dismiss() }
                }
            }
        }
    }

    private func resetPan() {
        offset = .zero
        baseOffset = .zero
    }
}

struct SchematicPlaceholder<Action: View>: View {
    let asset: ProcedureVisualAsset
    let tint: Color
    @ViewBuilder let action: () -> Action

    var body: some View {
        VStack(spacing: 12) {
            VStack(spacing: 12) {
                Image(systemName: asset.systemImage ?? "photo")
                    .font(.system(size: 44, weight: .medium))
                    .foregroundStyle(tint.opacity(0.7))
                    .frame(width: 80, height: 80)
                    .background(tint.opacity(0.08), in: RoundedRectangle(cornerRadius: AppLayout.mediaRadius, style: .continuous))

                Text("Image Pending")
                    .font(.caption2.weight(.semibold))
                    .foregroundStyle(.secondary)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 4)
                    .background(Color(.tertiarySystemFill), in: Capsule())
            }
            .accessibilityElement(children: .ignore)
            .accessibilityLabel("\(asset.kind.rawValue) image: \(asset.displayName). Image pending.")

            action()
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 20)
        .background(tint.opacity(0.04), in: RoundedRectangle(cornerRadius: AppLayout.mediaRadius, style: .continuous))
    }
}

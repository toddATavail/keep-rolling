import Cocoa

/// Whether the application is in verbose mode. This is true if the `--verbose`
/// or `-v` command-line argument is present.
let isVerbose = CommandLine.arguments.contains("--verbose")
	|| CommandLine.arguments.contains("-v")

// Wrapper function for conditional printing.
func verbosePrint(
	_ items: Any...,
	separator: String = " ",
	terminator: String = "\n"
) {
	if isVerbose
	{
		print(items, separator: separator, terminator: terminator)
	}
}

/// The view that captures the screen and allows the user to select a region.
class ScreenCaptureView: NSView
{
	/// The origin of the selection rectangle, which is the point where the
	/// user first clicked.
	var startPoint: NSPoint?

	/// The diagonal corner of the selection rectangle, which is the point where
	/// the user released the mouse button.
	var endPoint: NSPoint?

	/// The selection rectangle, which is the rectangle defined by `startPoint`
	/// and `endPoint`.
	var selectionRect: NSRect?

	override func mouseDown(with event: NSEvent)
	{
		startPoint = convert(event.locationInWindow, from: nil)
		verbosePrint("Mouse down at: \(startPoint!)")
	}

	override func mouseDragged(with event: NSEvent)
	{
		endPoint = convert(event.locationInWindow, from: nil)
		selectionRect = NSRect(x: min(startPoint!.x, endPoint!.x),
			y: min(startPoint!.y, endPoint!.y),
			width: abs(endPoint!.x - startPoint!.x),
			height: abs(endPoint!.y - startPoint!.y)
		)
		needsDisplay = true
		verbosePrint("Mouse dragged to: \(endPoint!)")
	}

	override func mouseUp(with event: NSEvent)
	{
		endPoint = convert(event.locationInWindow, from: nil)
		verbosePrint("Mouse up at: \(endPoint!)")
		DispatchQueue.main.async {
			NSApplication.shared.stop(nil)
		}
	}

	override func draw(_ dirtyRect: NSRect)
	{
		if let rect = selectionRect
		{
			NSColor.red.setStroke()
			NSBezierPath(rect: rect).stroke()
		}
	}
}

/// A custom window that can become the main window.
class CustomWindow: NSWindow
{
	override var canBecomeMain: Bool
	{
		return true
	}
}

verbosePrint("Starting application...")

let app = NSApplication.shared
app.setActivationPolicy(.accessory)

verbosePrint("Creating window...")

guard let screen = NSScreen.main else
{
	print("Error: Unable to get main screen")
	exit(1)
}

let window = CustomWindow(
	contentRect: screen.frame,
	styleMask: [.borderless, .fullSizeContentView],
	backing: .buffered,
	defer: false
)
window.level = .floating
window.backgroundColor = NSColor.clear.withAlphaComponent(0.1)
window.isOpaque = false

verbosePrint("Creating view...")

let view = ScreenCaptureView(frame: window.contentView!.bounds)
window.contentView?.addSubview(view)

verbosePrint("Making window key and visible...")

window.makeKeyAndOrderFront(nil)

verbosePrint("Setting up application delegate...")

/// The application delegate.
class AppDelegate: NSObject, NSApplicationDelegate
{
	func applicationDidFinishLaunching(_ notification: Notification)
	{
		verbosePrint("Application did finish launching")
	}
}

let delegate = AppDelegate()
app.delegate = delegate

verbosePrint("Running application...")

app.run()

/// The result is in `view.selectionRect`, which is the rectangle defined by
/// the user's selection. Print it if it exists, otherwise error out.
if let rect = view.selectionRect
{
	print(
		"""
			Selection: \
			\(Int(rect.origin.x)), \(Int(rect.origin.y)), \
			\(Int(rect.size.width)), \(Int(rect.size.height))
			"""
	)
}
else
{
	print("No selection was made")
}

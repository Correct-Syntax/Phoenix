# --------------------------------------------------------------------------------- #
# SUPERTOOLTIP wxPython IMPLEMENTATION
#
# Andrea Gavana, @ 07 October 2008
# Latest Revision: 04 Feb 2013, 21.00 GMT
#
#
# TODO List
#
# 1) Maybe add some more customization like multiline text
#    in the header and footer;
# 2) Check whether it's possible to use rounded corners and
#    shadows on the Mac
# 3) Split OnPaint() into smaller pieces to improve readability and
#    ability to redefine behaviour in subclasses
# 4) Extend text formatting capabilities
# 5) Make better use of links (right now it's difficult to click them without hiding tooltip)
#
# For all kind of problems, requests of enhancements and bug reports, please
# write to me at:
#
# andrea.gavana@gmail.com
# andrea.gavana@maerskoil.com
#
# Or, obviously, to the wxPython mailing list!!!
#
# Tags:         phoenix-port, documented, unittest, py3-port
#
# End Of Comments
# --------------------------------------------------------------------------------- #

"""
:class:`~wx.lib.agw.supertooltip.SuperToolTip` is a class that mimics the behaviour of :class:`TipWindow` and generic tooltip
windows, although it is a custom-drawn widget.


Description
===========

:class:`SuperToolTip` is a class that mimics the behaviour of :class:`TipWindow` and generic tooltip
windows, although it is a custom-drawn widget.

This class supports:

* Blended triple-gradient for the tooltip background;
* Header text and header image, with possibility to set the header font indipendently;
* Footer text and footer image, with possibility to set the footer font indipendently;
* Multiline text message in the tooltip body, plus an optional image as "body image";
* Bold lines and hyperlink lines in the tooltip body;
* A wide set of predefined drawing styles for the tooltip background;
* Drawing of separator lines after the header and/or before the footer;
* Rounded corners and shadows below the tooltip window (Windows XP only);
* Fade in/fade out effects (Windows XP only);
* User-settable delays for the delay after which the tooltip appears and the delay
  after which the tooltip is destroyed.

And a lot more. Check the demo for an almost complete review of the functionalities.


Usage
=====

Usage example::

    import wx
    import wx.lib.agw.supertooltip as STT

    class MyFrame(wx.Frame):

        def __init__(self, parent):

            wx.Frame.__init__(self, parent, -1, "SuperToolTip Demo")

            panel = wx.Panel(self)
            button = wx.Button(panel, -1, "I am the SuperToolTip target", pos=(100, 50))

            tip = STT.SuperToolTip("A nice tooltip message")

            tip.SetHeader("Hello World")
            tip.SetTarget(button)
            tip.SetDrawHeaderLine(True)

            tip.ApplyStyle("Office 2007 Blue")

            tip.SetDropShadow(True)


    # our normal wxApp-derived class, as usual

    app = wx.App(0)

    frame = MyFrame(None)
    app.SetTopWindow(frame)
    frame.Show()

    app.MainLoop()



Supported Platforms
===================

:class:`SuperToolTip` has been tested on the following platforms:
  * Windows (Windows XP).


Window Styles
=============

`No particular window styles are available for this class.`


Events Processing
=================

`No custom events are available for this class.`


License And Version
===================

:class:`SuperToolTip` is distributed under the wxPython license.

Latest Revision: Andrea Gavana @ 04 Feb 2013, 21.00 GMT

Version 0.5

"""

# Version Info
__version__ = "0.5"

import wx
import webbrowser

# Let's see if we can add few nice shadows to our tooltips (Windows only)
_libimported = None

if wx.Platform == "__WXMSW__":
    osVersion = wx.GetOsVersion()
    # Shadows behind menus are supported only in XP
    if osVersion[1] > 5 or (osVersion[1] == 5 and osVersion[2] >= 1):
        try:
            # Try Mark Hammond's win32all extensions
            import win32api
            import win32con
            import win32gui
            import winxpgui
            _libimported = "MH"
        except ImportError:
            _libimported = None
    else:
        _libimported = None


# Define a bunch of predefined colour schemes...

_colourSchemes = {
    "Beige": (wx.WHITE, wx.Colour(242, 242, 223), wx.Colour(198, 195, 160), wx.BLACK),
    "Blue": (wx.WHITE, wx.Colour(202, 220, 246), wx.Colour(150, 180, 222), wx.BLACK),
    "Blue 2": (wx.WHITE, wx.Colour(228, 236, 248), wx.Colour(198, 214, 235), wx.BLACK),
    "Blue 3": (wx.WHITE, wx.Colour(213, 233, 243), wx.Colour(151, 195, 216), wx.BLACK),
    "Blue 4": (wx.WHITE, wx.Colour(227, 235, 255), wx.Colour(102, 153, 255), wx.BLACK),
    "Blue Glass": (wx.Colour(182, 226, 253), wx.Colour(137, 185, 232), wx.Colour(188, 244, 253), wx.BLACK),
    "Blue Glass 2": (wx.Colour(192, 236, 255), wx.Colour(147, 195, 242), wx.Colour(198, 254, 255), wx.BLACK),
    "Blue Glass 3": (wx.Colour(212, 255, 255), wx.Colour(167, 215, 255), wx.Colour(218, 255, 255), wx.BLACK),
    "Blue Inverted": (wx.Colour(117, 160, 222), wx.Colour(167, 210, 240), wx.Colour(233, 243, 255), wx.BLACK),
    "Blue Shift": (wx.Colour(124, 178, 190), wx.Colour(13, 122, 153),  wx.Colour(0, 89, 116), wx.WHITE),
    "CodeProject": (wx.Colour(255, 250, 172), wx.Colour(255, 207, 157), wx.Colour(255, 153, 0), wx.BLACK),
    "Dark Gray": (wx.Colour(195, 195, 195), wx.Colour(168, 168, 168), wx.Colour(134, 134, 134), wx.WHITE),
    "Deep Purple": (wx.Colour(131, 128, 164), wx.Colour(112, 110, 143), wx.Colour(90, 88, 117), wx.WHITE),
    "Electric Blue": (wx.Colour(224, 233, 255), wx.Colour(135, 146, 251), wx.Colour(99, 109, 233), wx.BLACK),
    "Firefox": (wx.Colour(255, 254, 207), wx.Colour(254, 248, 125), wx.Colour(225, 119, 24), wx.BLACK),
    "Gold": (wx.Colour(255, 202, 0), wx.Colour(255, 202, 0), wx.Colour(255, 202, 0), wx.BLACK),
    "Gold Shift": (wx.Colour(178, 170, 107), wx.Colour(202, 180, 32), wx.Colour(162, 139, 1), wx.WHITE),
    "Gray": (wx.WHITE, wx.Colour(228, 228, 228), wx.Colour(194, 194, 194), wx.BLACK),
    "Green": (wx.Colour(234, 241, 223), wx.Colour(211, 224, 180), wx.Colour(182, 200, 150), wx.BLACK),
    "Green Shift": (wx.Colour(129, 184, 129), wx.Colour(13, 185, 15), wx.Colour(1, 125, 1), wx.WHITE),
    "Light Green": (wx.Colour(174, 251, 171), wx.Colour(145, 221, 146), wx.Colour(90, 176, 89), wx.BLACK),
    "NASA Blue": (wx.Colour(0, 91, 134), wx.Colour(0, 100, 150), wx.Colour(0, 105, 160), wx.WHITE),
    "Office 2007 Blue": (wx.WHITE, wx.Colour(242, 246, 251), wx.Colour(202, 218, 239), wx.Colour(76, 76, 76)),
    "Orange Shift": (wx.Colour(179, 120, 80), wx.Colour(183, 92, 19), wx.Colour(157, 73, 1), wx.WHITE),
    "Outlook Green": (wx.Colour(236, 242, 208), wx.Colour(219, 230, 187), wx.Colour(195, 210, 155), wx.BLACK),
    "Pale Green": (wx.Colour(249, 255, 248), wx.Colour(206, 246, 209), wx.Colour(148, 225, 155), wx.BLACK),
    "Pink Blush": (wx.Colour(255, 254, 255), wx.Colour(255, 231, 242), wx.Colour(255, 213, 233), wx.BLACK),
    "Pink Shift": (wx.Colour(202, 135, 188), wx.Colour(186, 8, 158), wx.Colour(146, 2, 116), wx.WHITE),
    "Pretty Pink": (wx.Colour(255, 240, 249), wx.Colour(253, 205, 217), wx.Colour(255, 150, 177), wx.BLACK),
    "Red": (wx.Colour(255, 183, 176), wx.Colour(253, 157, 143), wx.Colour(206, 88, 78), wx.BLACK),
    "Red Shift": (wx.Colour(186, 102, 102), wx.Colour(229, 23, 9), wx.Colour(182, 11, 1), wx.WHITE),
    "Silver": (wx.WHITE, wx.Colour(242, 242, 246), wx.Colour(212, 212, 224), wx.BLACK),
    "Silver 2": (wx.WHITE, wx.Colour(242, 242, 248), wx.Colour(222, 222, 228), wx.BLACK),
    "Silver Glass": (wx.Colour(158, 158, 158), wx.WHITE, wx.Colour(105, 105, 105), wx.BLACK),
    "Silver Inverted": (wx.Colour(161, 160, 186), wx.Colour(199, 201, 213), wx.WHITE, wx.BLACK),
    "Silver Inverted 2": (wx.Colour(181, 180, 206), wx.Colour(219, 221, 233), wx.WHITE, wx.BLACK),
    "Soylent Green": (wx.Colour(134, 211, 131), wx.Colour(105, 181, 106), wx.Colour(50, 136, 49), wx.WHITE),
    "Spring Green": (wx.Colour(154, 231, 151), wx.Colour(125, 201, 126), wx.Colour(70, 156, 69), wx.WHITE),
    "Too Blue": (wx.WHITE, wx.Colour(225, 235, 244), wx.Colour(188, 209, 226), wx.BLACK),
    "Totally Green": (wx.Colour(190, 230, 160), wx.Colour(190, 230, 160), wx.Colour(190, 230, 160), wx.BLACK),
    "XP Blue": (wx.Colour(119, 185, 236), wx.Colour(81, 144, 223), wx.Colour(36, 76, 171), wx.WHITE),
    "Yellow": (wx.Colour(255, 255, 220), wx.Colour(255, 231, 161), wx.Colour(254, 218, 108), wx.BLACK)
    }


def GetStyleKeys():
    """ Returns the predefined styles keywords. """

    schemes = sorted(_colourSchemes)
    return schemes


def MakeBold(font):
    """
    Makes a font bold. Utility method.

    :param `font`: the font to be made bold.
    """

    newFont = wx.Font(font.GetPointSize(), font.GetFamily(), font.GetStyle(),
                      wx.FONTWEIGHT_BOLD, font.GetUnderlined(), font.GetFaceName())

    return newFont


def ExtractLink(line):
    """
    Extract the link from an hyperlink line.

    :param `line`: the line of text to be processed.
    """

    line = line[4:]
    indxStart = line.find("{")
    indxEnd = line.find("}")
    hl = line[indxStart+1:indxEnd].strip()
    line = line[0:indxStart].strip()

    return line, hl


class ToolTipWindowBase(object):
    """ Base class for the different Windows and Mac implementation. """

    def __init__(self, parent, classParent):
        """
        Default class constructor.

        :param `parent`: the :class:`SuperToolTip` parent widget;
        :param `classParent`: the :class:`SuperToolTip` class object.
        """

        self._spacing = 6
        self._wasOnLink = False
        self._hyperlinkRect, self._hyperlinkWeb = [], []

        self._classParent = classParent
        self._alphaTimer = wx.Timer(self, wx.ID_ANY)

        # Bind the events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_TIMER, self.AlphaCycle)
        parent.Bind(wx.EVT_KILL_FOCUS, self.OnDestroy)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnDestroy)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnDestroy)


    def OnPaint(self, event):
        """
        Handles the ``wx.EVT_PAINT`` event for :class:`SuperToolTip`.

        If the `event` parameter is ``None``, calculates best size and returns it.

        :param `event`: a :class:`PaintEvent` event to be processed or ``None``.
        """

        maxWidth = 0
        if event is None:
            dc = wx.ClientDC(self)
        else:
            # Go with double buffering...
            dc = wx.BufferedPaintDC(self)

        frameRect = self.GetClientRect()
        x, y, width, _height = frameRect
        # Store the rects for the hyperlink lines
        self._hyperlinkRect, self._hyperlinkWeb = [], []
        classParent = self._classParent

        # Retrieve the colours for the blended triple-gradient background
        topColour, middleColour, bottomColour = classParent.GetTopGradientColour(), \
                                                classParent.GetMiddleGradientColour(), \
                                                classParent.GetBottomGradientColour()

        # Get the user options for header, bitmaps etc...
        drawHeader, drawFooter = classParent.GetDrawHeaderLine(), classParent.GetDrawFooterLine()
        topRect = wx.Rect(frameRect.x, frameRect.y, frameRect.width, frameRect.height/2)
        bottomRect = wx.Rect(frameRect.x, frameRect.y+frameRect.height/2, frameRect.width, frameRect.height/2+1)
        # Fill the triple-gradient
        dc.GradientFillLinear(topRect, topColour, middleColour, wx.SOUTH)
        dc.GradientFillLinear(bottomRect, middleColour, bottomColour, wx.SOUTH)

        header, headerBmp = classParent.GetHeader(), classParent.GetHeaderBitmap()
        headerFont, messageFont, footerFont, hyperlinkFont = classParent.GetHeaderFont(), classParent.GetMessageFont(), \
                                                             classParent.GetFooterFont(), classParent.GetHyperlinkFont()

        yPos = 0
        bmpXPos = 0
        bmpHeight = textHeight = bmpWidth = 0

        if headerBmp and headerBmp.IsOk():
            # We got the header bitmap
            bmpHeight, bmpWidth = headerBmp.GetHeight(), headerBmp.GetWidth()
            bmpXPos = self._spacing

        if header:
            # We got the header text
            dc.SetFont(headerFont)
            textWidth, textHeight = dc.GetTextExtent(header)
            maxWidth = max(bmpWidth+(textWidth+self._spacing*3), maxWidth)
        # Calculate the header height
        height = max(textHeight, bmpHeight)
        normalText = classParent.GetTextColour()
        if header:
            dc.SetTextForeground(normalText)
            dc.DrawText(header, bmpXPos+bmpWidth+self._spacing, (height-textHeight+self._spacing)/2)
        if headerBmp and headerBmp.IsOk():
            dc.DrawBitmap(headerBmp, bmpXPos, (height-bmpHeight+self._spacing)/2, True)

        if header or (headerBmp and headerBmp.IsOk()):
            yPos += height
            if drawHeader:
                # Draw the separator line after the header
                dc.SetPen(wx.GREY_PEN)
                dc.DrawLine(self._spacing, yPos+self._spacing, width-self._spacing, yPos+self._spacing)
                yPos += self._spacing

        maxWidth = max(bmpXPos + bmpWidth + self._spacing, maxWidth)
        # Get the big body image (if any)
        embeddedImage = classParent.GetBodyImage()
        bmpWidth = bmpHeight = -1
        if embeddedImage and embeddedImage.IsOk():
            bmpWidth, bmpHeight = embeddedImage.GetWidth(), embeddedImage.GetHeight()

        # A bunch of calculations to draw the main body message
        messageHeight = 0
        lines = classParent.GetMessage().split("\n")
        yText = yPos
        embImgPos = yPos
        hyperLinkText = wx.BLUE
        messagePos = self._getTextExtent(dc, lines[0] if lines else "")[1] // 2 + self._spacing
        for line in lines:
            # Loop over all the lines in the message
            if line.startswith("<hr>"):     # draw a line
                yText += self._spacing * 2
                dc.DrawLine(self._spacing, yText+self._spacing, width-self._spacing, yText+self._spacing)
            else:
                isLink = False
                dc.SetTextForeground(normalText)
                if line.startswith("</b>"):      # is a bold line
                    line = line[4:]
                    font = MakeBold(messageFont)
                    dc.SetFont(font)
                elif line.startswith("</l>"):    # is a link
                    dc.SetFont(hyperlinkFont)
                    isLink = True
                    line, hl = ExtractLink(line)
                    dc.SetTextForeground(hyperLinkText)
                else:
                    # Is a normal line
                    dc.SetFont(messageFont)

                textWidth, textHeight = self._getTextExtent(dc, line)

                messageHeight += textHeight

                xText = (bmpWidth + 2 * self._spacing) if bmpWidth > 0 else self._spacing
                yText += textHeight/2+self._spacing
                maxWidth = max(xText + textWidth + self._spacing, maxWidth)
                dc.DrawText(line, xText, yText)
                if isLink:
                    self._storeHyperLinkInfo(xText, yText, textWidth, textHeight, hl)

        toAdd = 0
        if bmpHeight > messageHeight:
            yPos += 2*self._spacing + bmpHeight
            toAdd = self._spacing
        else:
            yPos += messageHeight + 2*self._spacing

        yText = max(messageHeight, bmpHeight+2*self._spacing)
        if embeddedImage and embeddedImage.IsOk():
            # Draw the main body image
            dc.DrawBitmap(embeddedImage, self._spacing, embImgPos + (self._spacing * 2), True)

        footer, footerBmp = classParent.GetFooter(), classParent.GetFooterBitmap()
        bmpHeight = bmpWidth = textHeight = textWidth = 0
        bmpXPos = 0

        if footerBmp and footerBmp.IsOk():
            # Got the footer bitmap
            bmpHeight, bmpWidth = footerBmp.GetHeight(), footerBmp.GetWidth()
            bmpXPos = self._spacing

        if footer:
            # Got the footer text
            dc.SetFont(footerFont)
            textWidth, textHeight = dc.GetTextExtent(footer)

        if textHeight or bmpHeight:
            if drawFooter:
                # Draw the separator line before the footer
                dc.SetPen(wx.GREY_PEN)
                dc.DrawLine(self._spacing, yPos-self._spacing/2+toAdd,
                            width-self._spacing, yPos-self._spacing/2+toAdd)
        # Draw the footer and footer bitmap (if any)
        dc.SetTextForeground(normalText)
        height = max(textHeight, bmpHeight)
        yPos += toAdd
        if footer:
            toAdd = (height - textHeight + self._spacing) // 2
            dc.DrawText(footer, bmpXPos + bmpWidth + self._spacing, yPos + toAdd)
            maxWidth = max(bmpXPos + bmpWidth + (self._spacing*2) + textWidth, maxWidth)
        if footerBmp and footerBmp.IsOk():
            toAdd = (height - bmpHeight + self._spacing) / 2
            dc.DrawBitmap(footerBmp, bmpXPos, yPos + toAdd, True)
            maxWidth = max(footerBmp.GetSize().GetWidth() + bmpXPos, maxWidth)

        maxHeight = yPos + height + toAdd
        if event is None:
            return maxWidth, maxHeight


    @staticmethod
    def _getTextExtent(dc, line):
        textWidth, textHeight = dc.GetTextExtent(line)
        if textHeight == 0:
            _, textHeight = dc.GetTextExtent("a")
        return textWidth, textHeight

    def _storeHyperLinkInfo(self, hTextPos, vTextPos, textWidth, textHeight, linkTarget):
        # Store the hyperlink rectangle and link
        self._hyperlinkRect.append(wx.Rect(hTextPos, vTextPos, textWidth, textHeight))
        self._hyperlinkWeb.append(linkTarget)


    def OnEraseBackground(self, event):
        """
        Handles the ``wx.EVT_ERASE_BACKGROUND`` event for :class:`SuperToolTip`.

        :param `event`: a :class:`EraseEvent` event to be processed.

        :note: This method is intentionally empty to reduce flicker.
        """

        # This is intentionally empty to reduce flicker
        pass


    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for :class:`SuperToolTip`.

        :param `event`: a :class:`wx.SizeEvent` event to be processed.
        """

        self.Refresh()
        event.Skip()


    def OnMouseMotion(self, event):
        """
        Handles the ``wx.EVT_MOTION`` event for :class:`SuperToolTip`.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        x, y = event.GetPosition()
        for rect in self._hyperlinkRect:
            if rect.Contains((x, y)):
                # We are over one hyperlink...
                self.SetCursor(wx.Cursor(wx.CURSOR_HAND))
                self._wasOnLink = True
                return

        if self._wasOnLink:
            # Restore the normal cursor
            self._wasOnLink = False
            self.SetCursor(wx.NullCursor)


    def OnDestroy(self, event):
        """
        Handles the ``wx.EVT_LEFT_DOWN``, ``wx.EVT_LEFT_DCLICK`` and ``wx.EVT_KILL_FOCUS``
        events for :class:`SuperToolTip`. All these events destroy the :class:`SuperToolTip`,
        unless the user clicked on one hyperlink.

        :param `event`: a :class:`MouseEvent` or a :class:`FocusEvent` event to be processed.
        """

        if not isinstance(event, wx.MouseEvent):
            # We haven't clicked a link
            if self:  # Check if window still exists, Destroy might have been called manually (more than once)
                self.Destroy()
            return

        x, y = event.GetPosition()
        for indx, rect in enumerate(self._hyperlinkRect):
            if rect.Contains((x, y)):
                # Run the webbrowser with the clicked link
                webbrowser.open_new_tab(self._hyperlinkWeb[indx])
                return

        if self._classParent.GetUseFade():
            # Fade out...
            self.StartAlpha(False)
        else:
            self.Destroy()


    def StartAlpha(self, isShow):
        """
        Start the timer which set the alpha channel for :class:`SuperToolTip`.

        :param `isShow`: whether :class:`SuperToolTip` is being shown or deleted.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        if self._alphaTimer.IsRunning():
            return

        # Calculate starting alpha value and its step
        self.amount = (isShow and [0] or [255])[0]
        self.delta = (isShow and [5] or [-5])[0]
        # Start the timer
        self._alphaTimer.Start(30)


    def SetFont(self, font):
        """
        Sets the :class:`SuperToolTip` font globally.

        :param `font`: the font to set.
        """

        wx.PopupWindow.SetFont(self, font)
        self._classParent.InitFont()
        self.Invalidate()


    def Invalidate(self):
        """ Invalidate :class:`SuperToolTip` size and repaint it. """

        if not self._classParent.GetMessage():
            # No message yet...
            return

        self.CalculateBestSize()
        self.Refresh()


    def DropShadow(self, drop=True):
        """
        Adds a shadow under the window.

        :param `drop`: whether to drop a shadow or not.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        if not _libimported:
            # No Mark Hammond's win32all extension
            return

        if wx.Platform != "__WXMSW__":
            # This works only on Windows XP
            return

        hwnd = self.GetHandle()

        # Create a rounded rectangle region
        size = self.GetSize()
        if drop:
            if hasattr(win32gui, "CreateRoundRectRgn"):
                rgn = win32gui.CreateRoundRectRgn(0, 0, size.x, size.y, 9, 9)
                win32gui.SetWindowRgn(hwnd, rgn, True)

        CS_DROPSHADOW = 0x00020000
        # Load the user32 library
        if not hasattr(self, "_winlib"):
            self._winlib = win32api.LoadLibrary("user32")

        csstyle = win32api.GetWindowLong(hwnd, win32con.GCL_STYLE)
        if drop:
            if csstyle & CS_DROPSHADOW:
                return
            else:
                csstyle |= CS_DROPSHADOW     #Nothing to be done
        else:
            csstyle &= ~CS_DROPSHADOW

        # Drop the shadow underneath the window
        GCL_STYLE= -26
        cstyle= win32gui.GetClassLong(hwnd, GCL_STYLE)
        if drop:
            if cstyle & CS_DROPSHADOW == 0:
                win32api.SetClassLong(hwnd, GCL_STYLE, cstyle | CS_DROPSHADOW)
        else:
            win32api.SetClassLong(hwnd, GCL_STYLE, cstyle &~ CS_DROPSHADOW)


    def AlphaCycle(self, event):
        """
        Handles the ``wx.EVT_TIMER`` event for :class:`SuperToolTip`.

        :param `event`: a :class:`TimerEvent` event to be processed.
        """

        # Increase (or decrease) the alpha channel
        self.amount += self.delta

        if self.amount > 255 or self.amount < 0:
            # We're done, stop the timer
            self._alphaTimer.Stop()
            if self.amount < 0:
                # Destroy the SuperToolTip, we are fading out
                self.Destroy()
            return

        # Make the SuperToolTip more or less transparent
        self.MakeWindowTransparent(self.amount)
        if not self.IsShown():
            self.Show()


    def MakeWindowTransparent(self, amount):
        """
        Makes the :class:`SuperToolTip` window transparent.

        :param `amount`: the alpha channel value.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        if not _libimported:
            # No way, only Windows XP with Mark Hammond's win32all
            return

        # this API call is not in all SDKs, only the newer ones, so
        # we will runtime bind this
        if wx.Platform != "__WXMSW__":
            return

        hwnd = self.GetHandle()

        if not hasattr(self, "_winlib"):
            self._winlib = win32api.LoadLibrary("user32")

        pSetLayeredWindowAttributes = win32api.GetProcAddress(self._winlib,
                                                              "SetLayeredWindowAttributes")

        if pSetLayeredWindowAttributes is None:
            return

        exstyle = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if 0 == (exstyle & 0x80000):
            win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle | 0x80000)

        winxpgui.SetLayeredWindowAttributes(hwnd, 0, amount, 2)


    def CalculateBestSize(self):
        """ Calculates the :class:`SuperToolTip` window best size. """

        maxWidth, maxHeight = self.OnPaint(None)
        self.SetSize((maxWidth, maxHeight))


    def CalculateBestPosition(self,widget):
        x, y = wx.GetMousePosition()
        screen = wx.ClientDisplayRect()[2:]
        left, top = widget.ClientToScreen((0, 0))
        right, bottom = widget.ClientToScreen(widget.GetClientRect()[2:])
        size = self.GetSize()

        if x+size[0]>screen[0]:
            xpos = x-size[0]
        else:
            xpos = x

        if bottom+size[1]>screen[1]:
            ypos = top-size[1] + 6
        else:
            ypos = bottom + 6

        self.SetPosition((xpos,ypos))


# Handle Mac and Windows/GTK differences...

if wx.Platform == "__WXMAC__":

    class ToolTipWindow(wx.Frame, ToolTipWindowBase):
        """ Popup window that works on wxMac. """

        def __init__(self, parent, classParent):
            """
            Default class constructor.

            :param `parent`: the :class:`SuperToolTip` parent widget;
            :param `classParent`: the :class:`SuperToolTip` class object.
            """

            wx.Frame.__init__(self, parent, style=wx.NO_BORDER|wx.FRAME_FLOAT_ON_PARENT|wx.FRAME_NO_TASKBAR|wx.POPUP_WINDOW)
            # Call the base class
            ToolTipWindowBase.__init__(self, parent, classParent)

else:

    class ToolTipWindow(ToolTipWindowBase, wx.PopupWindow):
        """
        A simple :class:`PopupWindow` that holds fancy tooltips.
        Not available on Mac as :class:`PopupWindow` is not implemented there.
        """

        def __init__(self, parent, classParent):
            """
            Default class constructor.

            :param `parent`: the :class:`SuperToolTip` parent widget;
            :param `classParent`: the :class:`SuperToolTip` class object.
            """

            wx.PopupWindow.__init__(self, parent)
            # Call the base class
            ToolTipWindowBase.__init__(self, parent, classParent)


class SuperToolTip(object):
    """
    The main class for :class:`SuperToolTip`, which holds all the methods
    and setters/getters available to the user.
    """

    def __init__(self, message, bodyImage=wx.NullBitmap, header="", headerBmp=wx.NullBitmap,
                 footer="", footerBmp=wx.NullBitmap):
        """
        Default class constructor.

        :param `message`: the main message in :class:`SuperToolTip` body;
        :param `bodyImage`: the image in the :class:`SuperToolTip` body;
        :param `header`: the header text;
        :param `headerBmp`: the header bitmap;
        :param `footer`: the footer text;
        :param `footerBmp`: the footer bitmap.
        """

        self._superToolTip = None

        # Set all the initial options
        self.SetMessage(message)
        self.SetBodyImage(bodyImage)
        self.SetHeader(header)
        self.SetHeaderBitmap(headerBmp)
        self.SetFooter(footer)
        self.SetFooterBitmap(footerBmp)
        self._dropShadow = False
        self._useFade = False

        self._topLine = False
        self._bottomLine = False

        self.InitFont()

        # Get the running applications
        self._runningApp = wx.GetApp()
        self._runningApp.__superToolTip = True

        # Build a couple of timers...
        self._startTimer = wx.PyTimer(self.OnStartTimer)
        self._endTimer = wx.PyTimer(self.OnEndTimer)

        self.SetStartDelay()
        self.SetEndDelay()
        self.ApplyStyle("XP Blue")


    def SetTarget(self, widget):
        """
        Sets the target window for :class:`SuperToolTip`.

        :param `widget`: the widget to which :class:`SuperToolTip` is associated.
        """

        self._widget = widget

        self._widget.Bind(wx.EVT_ENTER_WINDOW, self.OnWidgetEnter)
        self._widget.Bind(wx.EVT_LEAVE_WINDOW, self.OnWidgetLeave)


    def GetTarget(self):
        """ Returns the target window for :class:`SuperToolTip`. """

        if not hasattr(self, "_widget"):
            raise Exception("\nError: the widget target for L{SuperToolTip} has not been set.")

        return self._widget


    def SetStartDelay(self, delay=1):
        """
        Sets the time delay (in seconds) after which the :class:`SuperToolTip` is created.

        :param `delay`: the delay in seconds.
        """

        self._startDelayTime = float(delay)


    def GetStartDelay(self):
        """ Returns the tim delay (in seconds) after which the :class:`SuperToolTip` is created."""

        return self._startDelayTime


    def SetEndDelay(self, delay=1e6):
        """
        Sets the delay time (in seconds) after which the :class:`SuperToolTip` is destroyed.

        :param `delay`: the delay in seconds.
        """

        self._endDelayTime = float(delay)


    def GetEndDelay(self):
        """ Returns the delay time (in seconds) after which the :class:`SuperToolTip` is destroyed."""

        return self._endDelayTime


    def OnWidgetEnter(self, event):
        """
        Starts the :class:`SuperToolTip` timer for creation, handles the ``wx.EVT_ENTER_WINDOW`` event.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if self._superToolTip:
            # Not yet created
            return

        if not self._runningApp.__superToolTip:
            # The running app doesn't want tooltips...
            return

        if not self._widget.GetTopLevelParent().IsActive():
            self._startTimer.Stop()
            return

        if self._startTimer.IsRunning():
            # We are already running
            event.Skip()
            return
        self._startTimer.Start(self._startDelayTime*1000)
        event.Skip()


    def OnWidgetLeave(self, event):
        """
        Handles the ``wx.EVT_LEAVE_WINDOW`` event for the target widgets.

        :param `event`: a :class:`MouseEvent` event to be processed.
        """

        if self._superToolTip:
            if self.GetUseFade():
                # Fade out...
                self._superToolTip.StartAlpha(False)
            else:
                self._superToolTip.Destroy()

        self._startTimer.Stop()
        self._endTimer.Stop()

        event.Skip()

    def GetTipWindow(self):
        """ Return the TipWindow, will return None if not yet created """

        return self._superToolTip


    def OnStartTimer(self):
        """ The creation time has expired, create the :class:`SuperToolTip`. """

        # target widget might already be destroyed
        if not self._widget:
            self._startTimer.Stop()
            return

        tip = ToolTipWindow(self._widget, self)
        self._superToolTip = tip
        self._superToolTip.CalculateBestSize()
        self._superToolTip.CalculateBestPosition(self._widget)
        self._superToolTip.DropShadow(self.GetDropShadow())

        if self.GetUseFade():
            self._superToolTip.StartAlpha(True)
        else:
            self._superToolTip.Show()

        self._startTimer.Stop()
        self._endTimer.Start(self._endDelayTime*1000)


    def OnEndTimer(self):
        """ The show time for :class:`SuperToolTip` has expired, destroy the :class:`SuperToolTip`. """

        if self._superToolTip:
            if self.GetUseFade():
                self._superToolTip.StartAlpha(False)
            else:
                self._superToolTip.Destroy()

        self._endTimer.Stop()


    def DoShowNow(self):
        """ Create the :class:`SuperToolTip` immediately. """

        if self._superToolTip:
            # need to destroy it if already exists,
            # otherwise we might end up with many of them
            self._superToolTip.Destroy()

        tip = ToolTipWindow(self._widget, self)
        self._superToolTip = tip
        self._superToolTip.CalculateBestSize()
        self._superToolTip.CalculateBestPosition(self._widget)
        self._superToolTip.DropShadow(self.GetDropShadow())

        # need to stop this, otherwise we get into trouble when leaving the window
        self._startTimer.Stop()

        if self.GetUseFade():
            self._superToolTip.StartAlpha(True)
        else:
            self._superToolTip.Show()

        self._endTimer.Start(self._endDelayTime*1000)


    def DoHideNow(self):
        """
        Dismiss the :class:`SuperToolTip` window immediately.

        .. versionadded:: 0.9.6
        """

        if self._superToolTip:
            if self.GetUseFade():
                # Fade out...
                self._superToolTip.StartAlpha(False)
            else:
                self._superToolTip.Destroy()

        self._startTimer.Stop()
        self._endTimer.Stop()


    def Show(self, show=True):
        """
        Shows or hides the window.

        You may need to call `Raise` for a top level window if you want to bring it to
        top, although this is not needed if :meth:`~SuperToolTip.Show` is called immediately after the frame creation.

        :param bool `show`: ``True`` to show the :class:`SuperToolTip` window, ``False`` to hide it.

        :return: ``True`` if the window has been shown or hidden or ``False`` if nothing was done
         because it already was in the requested state.

        .. note::

           Notice that the default state of newly created top level windows is hidden (to allow
           you to create their contents without flicker) unlike for all the other, not derived from
           :class:`TopLevelWindow`, windows that are by default created in the shown state.


        .. versionadded:: 0.9.5
        """

        if show and self._superToolTip is None:
            self.DoShowNow()
            return True
        elif not show and self._superToolTip is not None:
            self.DoHideNow()
            return True
        return False


    def Update(self):
        """
        Calling this method immediately repaints the invalidated area of the window and all of its
        children recursively (this normally only happens when the flow of control returns to the
        event loop).

        :note: Notice that this function doesn't invalidate any area of the window so nothing happens
         if nothing has been invalidated (i.e. marked as requiring a redraw). Use `Refresh` first if
         you want to immediately redraw the window unconditionally.

        .. versionadded:: 0.9.5
        """

        if self._superToolTip:
            self._superToolTip.Update()


    def OnDestroy(self, event):
        """ Handles the :class:`SuperToolTip` target destruction. """

        if self._superToolTip:
            # Unbind the events!
            self._widget.Unbind(wx.EVT_LEAVE_WINDOW)
            self._widget.Unbind(wx.EVT_ENTER_WINDOW)

            self._superToolTip.Destroy()
            del self._superToolTip
            self._superToolTip = None


    def SetHeaderBitmap(self, bmp):
        """
        Sets the header bitmap for :class:`SuperToolTip`.

        :param `bmp`: the header bitmap, a valid :class:`wx.Bitmap` object.
        """

        self._headerBmp = bmp
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetHeaderBitmap(self):
        """ Returns the header bitmap. """

        return self._headerBmp


    def SetHeader(self, header):
        """
        Sets the header text.

        :param `header`: the header text to display.
        """

        self._header = header
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetHeader(self):
        """ Returns the header text. """

        return self._header


    def SetDrawHeaderLine(self, draw):
        """
        Sets whether to draw a separator line after the header or not.

        :param `draw`: ``True`` to draw a separator line after the header, ``False``
         otherwise.
        """

        self._topLine = draw
        if self._superToolTip:
            self._superToolTip.Refresh()


    def GetDrawHeaderLine(self):
        """ Returns whether the separator line after the header is drawn or not. """

        return self._topLine


    def SetBodyImage(self, bmp):
        """
        Sets the main body bitmap for :class:`SuperToolTip`.

        :param `bmp`: the body bitmap, a valid :class:`wx.Bitmap` object.
        """

        self._embeddedImage = bmp
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetBodyImage(self):
        """ Returns the main body bitmap used in :class:`SuperToolTip`. """

        return self._embeddedImage


    def SetDrawFooterLine(self, draw):
        """
        Sets whether to draw a separator line before the footer or not.

        :param `draw`: ``True`` to draw a separator line before the footer, ``False``
         otherwise.
        """

        self._bottomLine = draw
        if self._superToolTip:
            self._superToolTip.Refresh()


    def GetDrawFooterLine(self):
        """ Returns whether the separator line before the footer is drawn or not. """

        return self._bottomLine


    def SetFooterBitmap(self, bmp):
        """
        Sets the footer bitmap for :class:`SuperToolTip`.

        :param `bmp`: the footer bitmap, a valid :class:`wx.Bitmap` object.
        """

        self._footerBmp = bmp
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetFooterBitmap(self):
        """ Returns the footer bitmap. """

        return self._footerBmp


    def SetFooter(self, footer):
        """
        Sets the footer text.

        :param `footer`: the footer text to display.
        """

        self._footer = footer
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetFooter(self):
        """ Returns the footer text. """

        return self._footer


    def SetMessage(self, message):
        """
        Sets the main body message for :class:`SuperToolTip`.

        :param `message`: the message to display in the body.
        """

        self._message = message
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetMessage(self):
        """ Returns the main body message in :class:`SuperToolTip`. """

        return self._message


    def SetTopGradientColour(self, colour):
        """
        Sets the top gradient colour for :class:`SuperToolTip`.

        :param `colour`: the colour to use as top colour, a valid :class:`wx.Colour` object.
        """

        self._topColour = colour
        if self._superToolTip:
            self._superToolTip.Refresh()


    def SetMiddleGradientColour(self, colour):
        """
        Sets the middle gradient colour for :class:`SuperToolTip`.

        :param `colour`: the colour to use as middle colour, a valid :class:`wx.Colour` object.
        """

        self._middleColour = colour
        if self._superToolTip:
            self._superToolTip.Refresh()


    def SetBottomGradientColour(self, colour):
        """
        Sets the bottom gradient colour for :class:`SuperToolTip`.

        :param `colour`: the colour to use as bottom colour, a valid :class:`wx.Colour` object.
        """

        self._bottomColour = colour
        if self._superToolTip:
            self._superToolTip.Refresh()


    def SetTextColour(self, colour):
        """
        Sets the text colour for :class:`SuperToolTip`.

        :param `colour`: the colour to use as text colour, a valid :class:`wx.Colour` object.
        """

        self._textColour = colour
        if self._superToolTip:
            self._superToolTip.Refresh()


    def GetTopGradientColour(self):
        """ Returns the top gradient colour. """

        return self._topColour


    def GetMiddleGradientColour(self):
        """ Returns the middle gradient colour. """

        return self._middleColour


    def GetBottomGradientColour(self):
        """ Returns the bottom gradient colour. """

        return self._bottomColour


    def GetTextColour(self):
        """ Returns the text colour. """

        return self._textColour


    SetTopGradientColor = SetTopGradientColour
    SetMiddleGradientColor = SetMiddleGradientColour
    SetBottomGradientColor = SetBottomGradientColour
    GetTopGradientColor = GetTopGradientColour
    GetMiddleGradientColor = GetMiddleGradientColour
    GetBottomGradientColor = GetBottomGradientColour
    SetTextColor = SetTextColour
    GetTextColor = GetTextColour


    def InitFont(self):
        """ Initalizes the fonts for :class:`SuperToolTip`. """

        self._messageFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._headerFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._headerFont.SetWeight(wx.FONTWEIGHT_BOLD)
        self._footerFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._footerFont.SetWeight(wx.FONTWEIGHT_BOLD)
        self._hyperlinkFont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self._hyperlinkFont.SetWeight(wx.FONTWEIGHT_BOLD)
        self._hyperlinkFont.SetUnderlined(True)


    def SetMessageFont(self, font):
        """
        Sets the font for the main body message.

        :param `font`: the font to use for the main body message, a valid :class:`wx.Font`
         object.
        """

        self._messageFont = font
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def SetHeaderFont(self, font):
        """
        Sets the font for the header text.

        :param `font`: the font to use for the header text, a valid :class:`wx.Font`
         object.
        """

        self._headerFont = font
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def SetFooterFont(self, font):
        """
        Sets the font for the footer text.

        :param `font`: the font to use for the footer text, a valid :class:`wx.Font`
         object.
        """

        self._footerFont = font
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def SetHyperlinkFont(self, font):
        """
        Sets the font for the hyperlink text.

        :param `font`: the font to use for the hyperlink text, a valid :class:`wx.Font`
         object.
        """

        self._hyperlinkFont = font
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetMessageFont(self):
        """ Returns the font used in the main body message. """

        return self._messageFont


    def GetHeaderFont(self):
        """ Returns the font used for the header text. """

        return self._headerFont


    def GetFooterFont(self):
        """ Returns the font used for the footer text. """

        return self._footerFont


    def GetHyperlinkFont(self):
        """ Returns the font used for the hyperlink text. """

        return self._hyperlinkFont


    def SetDropShadow(self, drop):
        """
        Whether to draw a shadow below :class:`SuperToolTip` or not.

        :param `drop`: ``True`` to drop a shadow below the control, ``False`` otherwise.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        self._dropShadow = drop
        if self._superToolTip:
            self._superToolTip.Invalidate()


    def GetDropShadow(self):
        """
        Returns whether a shadow below :class:`SuperToolTip` is drawn or not.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        return self._dropShadow


    def SetUseFade(self, fade):
        """
        Whether to use a fade in/fade out effect or not.

        :param `fade`: ``True`` to use a fade in/fade out effect, ``False`` otherwise.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        self._useFade = fade


    def GetUseFade(self):
        """
        Returns whether a fade in/fade out effect is used or not.

        :note: This method is available only on Windows and requires Mark Hammond's
         pywin32 package.
        """

        return self._useFade


    def ApplyStyle(self, style):
        """
        Applies none of the predefined styles.

        :param `style`: one of the predefined styles available at the
         beginning of the module.
        """

        if style not in _colourSchemes:
            raise Exception("Invalid style '%s' selected"%style)

        top, middle, bottom, text = _colourSchemes[style]
        self._topColour = top
        self._middleColour = middle
        self._bottomColour = bottom
        self._textColour = text

        if self._superToolTip:
            self._superToolTip.Refresh()


    def EnableTip(self, enable=True):
        """
        Globally (application-wide) enables/disables :class:`SuperToolTip`.

        :param `enable`: ``True`` to enable :class:`SuperToolTip` globally, ``False`` otherwise.
        """

        wx.GetApp().__superToolTip = enable
        if not enable and self._superToolTip:
            self.DoHideNow()
            del self._superToolTip
            self._superToolTip = None


    def IsEnabled(self):
        """
        Returns ``True`` when :class:`SuperToolTip` is globally enabled, ``False`` otherwise.

        .. versionadded:: 0.9.6
        """

        return wx.GetApp().__superToolTip

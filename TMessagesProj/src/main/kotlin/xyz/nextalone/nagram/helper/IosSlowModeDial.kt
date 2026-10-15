package xyz.nextalone.nagram.helper

import android.graphics.Canvas
import android.graphics.Paint
import android.text.TextPaint
import org.telegram.messenger.AndroidUtilities
import org.telegram.ui.ActionBar.Theme
import kotlin.math.cos
import kotlin.math.sin

object IosSlowModeDial {

    private const val TICK_COUNT = 60
    private const val MAJOR_TICK_STEP = 5
    private const val COMPACT_DIAL_SIZE_DP = 38f
    private const val COMPACT_DIAL_MARGIN_DP = 3f
    private const val RING_WIDTH_DP = 0.5f
    private const val RING_GAP_DP = 1f
    private const val TICK_OFFSET_DP = 1f
    private const val MAJOR_TICK_LENGTH_DP = 2.25f
    private const val MINOR_TICK_LENGTH_DP = 1.5f
    private const val MAJOR_TICK_WIDTH_DP = 1.1f
    private const val MINOR_TICK_WIDTH_DP = 0.75f
    private const val TEXT_SIZE_DP = 12.5f
    private const val TEXT_SIZE_LONG_DP = 10f
    private const val COMPACT_TEXT_SIZE_DP = 11f
    private const val COMPACT_TEXT_SIZE_LONG_DP = 9.5f

    private val tickPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
    }
    private val backgroundPaint = Paint(Paint.ANTI_ALIAS_FLAG)
    private val textPaint = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
        typeface = AndroidUtilities.bold()
        fontFeatureSettings = "tnum"
    }

    private val tickUnitX = FloatArray(TICK_COUNT)
    private val tickUnitY = FloatArray(TICK_COUNT)

    private var cachedText: CharSequence? = null
    private var cachedIsLongText = false
    private var cachedIsFullSize = true
    private var cachedDensity = 0f
    private var cachedTextWidth = 0f
    private var cachedTextCenterOffset = 0f

    init {
        for (i in 0 until TICK_COUNT) {
            val angle = i.toDouble() / TICK_COUNT * 2.0 * Math.PI - Math.PI / 2.0
            tickUnitX[i] = cos(angle).toFloat()
            tickUnitY[i] = sin(angle).toFloat()
        }
    }

    fun draw(
        canvas: Canvas,
        slotWidth: Float,
        slotHeight: Float,
        leftSeconds: Int,
        secondFraction: Float,
        periodSeconds: Int,
        isFullSize: Boolean,
        timeText: CharSequence?,
        iconColor: Int,
        dialBackgroundColor: Int,
    ) {
        val text = timeText ?: return
        val radius = (if (isFullSize) slotHeight else AndroidUtilities.dp(COMPACT_DIAL_SIZE_DP).toFloat()) / 2f
        val margin = if (isFullSize) 0 else AndroidUtilities.dp(COMPACT_DIAL_MARGIN_DP)
        val cx = slotWidth - margin - radius
        val cy = slotHeight - margin - radius

        backgroundPaint.color = dialBackgroundColor
        canvas.drawCircle(cx, cy, radius, backgroundPaint)

        val backgroundIsLight = AndroidUtilities.computePerceivedBrightness(dialBackgroundColor) >= 0.5f
        val dimColor = Theme.multAlpha(iconColor, if (backgroundIsLight) 0.5f else 0.38f)

        if (periodSeconds > 0) {
            val activeTicksFloat = ((leftSeconds - secondFraction) / periodSeconds).coerceIn(0f, 1f) * TICK_COUNT
            val fullActiveTicks = activeTicksFloat.toInt()
            val meltingTickAlpha = activeTicksFloat - fullActiveTicks

            tickPaint.color = dimColor
            tickPaint.strokeWidth = AndroidUtilities.dp(RING_WIDTH_DP).toFloat()
            canvas.drawCircle(cx, cy, radius - AndroidUtilities.dp(TICK_OFFSET_DP), tickPaint)

            val outerRadius = radius - AndroidUtilities.dp(TICK_OFFSET_DP) - AndroidUtilities.dp(RING_GAP_DP)
            val majorInnerRadius = outerRadius - AndroidUtilities.dp(MAJOR_TICK_LENGTH_DP)
            val minorInnerRadius = outerRadius - AndroidUtilities.dp(MINOR_TICK_LENGTH_DP)
            val majorWidth = AndroidUtilities.dp(MAJOR_TICK_WIDTH_DP).toFloat()
            val minorWidth = AndroidUtilities.dp(MINOR_TICK_WIDTH_DP).toFloat()
            for (i in 0 until TICK_COUNT) {
                val isMajor = i % MAJOR_TICK_STEP == 0
                val innerRadius = if (isMajor) majorInnerRadius else minorInnerRadius
                tickPaint.color = when {
                    i < fullActiveTicks -> iconColor
                    i == fullActiveTicks && meltingTickAlpha > 0f -> Theme.multAlpha(iconColor, meltingTickAlpha)
                    else -> dimColor
                }
                tickPaint.strokeWidth = if (isMajor) majorWidth else minorWidth
                canvas.drawLine(
                    cx + tickUnitX[i] * outerRadius,
                    cy + tickUnitY[i] * outerRadius,
                    cx + tickUnitX[i] * innerRadius,
                    cy + tickUnitY[i] * innerRadius,
                    tickPaint,
                )
            }
        }

        val isLongText = text.length >= 5
        if (text != cachedText || isLongText != cachedIsLongText || isFullSize != cachedIsFullSize || AndroidUtilities.density != cachedDensity) {
            cachedText = text
            cachedIsLongText = isLongText
            cachedIsFullSize = isFullSize
            cachedDensity = AndroidUtilities.density
            val textSizeDp = when {
                isFullSize && isLongText -> TEXT_SIZE_LONG_DP
                isFullSize -> TEXT_SIZE_DP
                isLongText -> COMPACT_TEXT_SIZE_LONG_DP
                else -> COMPACT_TEXT_SIZE_DP
            }
            textPaint.textSize = AndroidUtilities.dp(textSizeDp).toFloat()
            cachedTextWidth = textPaint.measureText(text.toString())
            cachedTextCenterOffset = (textPaint.descent() + textPaint.ascent()) / 2f
        }
        textPaint.color = iconColor
        canvas.drawText(text, 0, text.length, cx - cachedTextWidth / 2f, cy - cachedTextCenterOffset, textPaint)
    }
}

# Base build (TURBO_BASE=1): disputable feature MECHANICS must be fully stripped by R8.
# Fails the build if any listed class survives — spec tos-base-builds BR-2/UC-5.
# Out of contract (allowed dead-weight, unreachable in base): Room schema classes kept
# by room-runtime consumer rules; fragment Activity shells kept by ActionBar/BaseFragment
# override keeps (they pin AyuFilter/ReactionFilter bodies with them); all LIVE call
# sites of every disputable feature are gated on BuildVars.TURBO_BASE.
-checkdiscard class com.radolyn.ayugram.messages.**
-checkdiscard class com.radolyn.ayugram.utils.**
-checkdiscard class com.radolyn.ayugram.proprietary.**
-checkdiscard class xyz.nextalone.nagram.helper.ProtectedForward
-checkdiscard class xyz.nextalone.nagram.helper.LocalPremiumStatusHelper**
-checkdiscard class xyz.nextalone.nagram.helper.IosSlowModeDial

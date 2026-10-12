package tw.nekomimi.nekogram.helpers;

import org.telegram.messenger.NotificationsController;

import xyz.nextalone.nagram.NaConfig;

public class AutoMuteHelper {

    public static void muteJoinedChat(int currentAccount, long chatId) {
        if (NaConfig.INSTANCE.getAutoMuteOnJoin().Bool()) {
            NotificationsController.getInstance(currentAccount).muteDialog(-chatId, 0, true);
        }
    }
}

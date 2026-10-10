package tw.nekomimi.nekogram.helpers;

import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.Utilities;
import org.telegram.tgnet.ConnectionsManager;
import org.telegram.tgnet.TLRPC;

import java.util.ArrayList;
import java.util.regex.Pattern;

public class SearchFromIdHelper {

    private static final String[] SEARCH_FROM_ID_PREFIXES = {"from:", "id:"};
    private static final Pattern USER_ID_DIGITS = Pattern.compile("[1-9]\\d{0,9}");

    public static class Result {
        public final long userId;
        public final String textQuery;

        public Result(long userId, String textQuery) {
            this.userId = userId;
            this.textQuery = textQuery;
        }
    }

    public static Result parseSearchFromId(String query, boolean allowBareUserId) {
        if (query == null) {
            return null;
        }
        for (String prefix : SEARCH_FROM_ID_PREFIXES) {
            if (query.length() > prefix.length() && query.regionMatches(true, 0, prefix, 0, prefix.length())) {
                String operand = query.substring(prefix.length());
                int spaceIndex = operand.indexOf(' ');
                String digits = spaceIndex >= 0 ? operand.substring(0, spaceIndex) : operand;
                if (USER_ID_DIGITS.matcher(digits).matches()) {
                    String textQuery = spaceIndex >= 0 ? operand.substring(spaceIndex + 1).trim() : "";
                    return new Result(Long.parseLong(digits), textQuery);
                }
            }
        }
        if (allowBareUserId && USER_ID_DIGITS.matcher(query).matches()) {
            return new Result(Long.parseLong(query), "");
        }
        return null;
    }

    public static void resolveUserById(long userId, int currentAccount, Utilities.Callback<TLRPC.User> callback) {
        TLRPC.TL_users_getUsers req = new TLRPC.TL_users_getUsers();
        TLRPC.TL_inputUser inputUser = new TLRPC.TL_inputUser();
        inputUser.user_id = userId;
        req.id.add(inputUser);
        ConnectionsManager.getInstance(currentAccount).sendRequest(req, (response, error) -> AndroidUtilities.runOnUIThread(() -> {
            TLRPC.User resolvedUser = null;
            if (response instanceof org.telegram.tgnet.Vector) {
                ArrayList<?> resolvedObjects = ((org.telegram.tgnet.Vector) response).objects;
                for (int i = 0; i < resolvedObjects.size(); i++) {
                    Object responseObject = resolvedObjects.get(i);
                    if (responseObject instanceof TLRPC.User && !(responseObject instanceof TLRPC.TL_userEmpty)) {
                        resolvedUser = (TLRPC.User) responseObject;
                        break;
                    }
                }
            }
            if (resolvedUser != null) {
                MessagesController.getInstance(currentAccount).putUser(resolvedUser, false);
            }
            callback.run(resolvedUser);
        }));
    }
}

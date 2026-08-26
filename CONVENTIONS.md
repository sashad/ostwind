This project is an odoo 18 community version application.

Use tabulation width 4 spaces in js files.

Use ES6 JS syntax in js files.

In Odoo 18, the <list> tag replaces <tree> for defining list views in XML, while maintaining the same functionality. The OCA updated modules like iot_oca to use <list> in Odoo 18, aligning with the framework’s new terminology, but both tags still work for backward compatibility.

Getting an user info in 18-th version:
```javascript
    // Retrieve user-related information from the session
    import { session } from "@web/session";

    const {
        home_action_id: homeActionId,
        is_admin: isAdmin,
        is_internal_user: isInternalUser,
        is_system: isSystem,
        name,
        partner_id: partnerId,
        show_effect: showEffect,
        uid: userId,
        username: login,
        user_context: context,
        user_settings,
        partner_write_date: writeDate,
    } = session;
```
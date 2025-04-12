Ext._define('judicial.diligences.GiveBackWindow', {
    extend: 'judicial.diligences.DeliveryAttemptWindow',

    getMainFields: function() {
        return [];
    },

    save: function (skipConfirm) {
        if(skipConfirm)
            judicial.diligences.GiveBackWindow.superclass.save.call(this, {});
        else
        Ext.Msg.show({
            title: 'Confirmação ...',
            icon: Ext.Msg.QUESTION,
            buttons: Ext.Msg.YESNO,
            msg: 'Tem certeza de que deseja devolver essa diligência?',
            scope: this,
            fn: function(btn) {
                if (btn == "no") return;
                judicial.diligences.GiveBackWindow.superclass.save.call(this, {});
            }
        });
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            disableSave: true,
            title: 'Devolução de Diligência',
        });

        judicial.diligences.GiveBackWindow.superclass.constructor.call(this, cfg);
        this.getCancelDeliveryField().setValue(true);
        this.getCancelDeliveryField().setVisible(false);
    }
});

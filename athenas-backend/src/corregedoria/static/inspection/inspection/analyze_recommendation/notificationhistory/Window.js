Ext._define('corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.inspection.inspection.follow_recommendation.notificationhistory.Restful',

    width: 600,

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [

                ]
            });

        return this._formPanel;
    },
});

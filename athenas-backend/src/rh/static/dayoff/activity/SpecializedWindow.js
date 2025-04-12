Ext._define('rh.dayoff.activity.SpecializedWindow', {
    extend: 'rh.dayoff.activity.Window',

    width: 600,

    getWindowConfig: function (cfg) {
        if (cfg.type_window == 'employee') {
            if (cfg.actionCustom == 'book') {
                return [
                    this.getInformation(cfg),
                    this.getNewBookField(),
                    this.getNewBook()
                ]
            } else {
                return [
                    this.getInformation(cfg),
                    this.getBookedUsufructsFieldSet(cfg),
                    this.getNewBookField(),
                    this.getNewBook(),
                    this.getJustificationField(),
                ]
            }
        }

        if (cfg.type_window == 'admin') {
            if (cfg.actionCustom == 'book') {
                return [
                    this.getInformation(cfg),
                    this.getNewBookField(),
                    this.getBosses(),
                    this.getNewBook()
                ]
            }
            else {
                return [
                    this.getInformation(cfg),
                    this.getBookedUsufructsFieldSet(cfg),
                    this.getNewBookField(),
                    this.getNewBook(),
                    this.getBosses(),
                    this.getJustificationField(),
                    this.getAttachmentField(),
                ]
            }
        }
    },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: this.getWindowConfig(cfg)
            });

        return this._formPanel;
    }
});

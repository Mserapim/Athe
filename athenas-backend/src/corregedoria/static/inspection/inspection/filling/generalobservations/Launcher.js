
Ext._define('corregedoria.inspection.inspection.filling.generalobservations.Launcher', {
    extend: 'Ext.Panel',

    getEditor: function (cfg) {
        if (!this._ckeditoField) {
            cfg = core.nullValue(cfg, {});
            Ext.apply(cfg, {
                allowBlank: true,
                startupFocus: false,
                editorConfig: {
                    forcePasteAsPlainText: true
                },
            });
            this._ckeditoField = Ext._create('toolkit.fields.CKEditor', cfg);
        }
        return this._ckeditoField;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'OBSERVAÇÕES GERAIS',
            layout: 'form',
            frame: true,
            height: 535,
            border: false,
            autoScroll: true,
            overflow: 'auto',
            bodyStyle: 'padding: 5px',
            labelWidth: 1,
            items: [
                this.getEditor({
                    name: 'go_generalobservations',
                    height: 525,
                    width: 1145
                })
            ],
        });

        Ext.apply(cfg, {

        });

        corregedoria.inspection.inspection.filling.generalobservations.Launcher.superclass.constructor.call(this, cfg);

    }
});

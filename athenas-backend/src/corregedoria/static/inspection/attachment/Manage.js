/**
 *
 **/
Ext._define('corregedoria.inspection.attachment.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getNewAttachment: function() {
        if(!this._attachment) {
            this._attachment = Ext._create('corregedoria.inspection.attachment.AttachmentGrid', {
                region: 'center',
            });
        }

        return this._attachment;
    },



    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Anexos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getNewAttachment(),
                ]
            }
        );

        corregedoria.inspection.attachment.Manage.superclass.constructor.call(this, cfg);
    }
});

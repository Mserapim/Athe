/**
 *
 **/
Ext._define('cif.attachment.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getAttachment: function() {
        if(!this._attachment) {
            this._attachment = Ext._create('cif.attachment.AttachmentGrid', {
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
                    this.getAttachment(),
                ]
            }
        );

        cif.attachment.Manage.superclass.constructor.call(this, cfg);
    }
});

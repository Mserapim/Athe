/**
 *
 **/
Ext._define('cif.address.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getAddres: function() {
        if(!this.address) {
            this.address = Ext._create('cif.address.AddressGrid', {
                region: 'center',
            });
        }

        return this.address;
    },



    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Endereços'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getAddres(),
                ]
            }
        );

        cif.address.Manage.superclass.constructor.call(this, cfg);
    }
});

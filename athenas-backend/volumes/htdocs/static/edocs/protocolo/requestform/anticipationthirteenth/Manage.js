Ext._define('edocs.protocolo.requestform.anticipationthirteenth.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function () {
        if (this._grid) {
            return this._grid;
        }

        this._grid = Ext._create('edocs.protocolo.requestform.anticipationthirteenth.Grid', {
            region: 'center'
        });

        return this._grid;
    },

    constructor: function (cfg) {
        try {
            cfg = cfg || {};

            Ext.applyIf(cfg, {
                title: 'Formulário'
            });

            Ext.apply(cfg, {
                layout: 'border',
                items: this.getGrid()
            });

            edocs
              .protocolo
              .requestform
              .anticipationthirteenth
              .Manage
              .superclass
              .constructor
              .call(this, cfg);
        } catch (e) {
            console.error(e);
        }
    }
});

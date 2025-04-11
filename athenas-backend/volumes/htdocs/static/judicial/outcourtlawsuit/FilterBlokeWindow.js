/**
 *
 **/

Ext._define('judicial.outcourtlawsuit.FilterBlokeWindow', {
    extend: 'judicial.outcourtlawsuit.FilterBaseWindow',

    width: 650,

    properties: [
        {
            stage: 1003,
            property: 'blokes__bloke',
            propertyAliases: [
                'blokes__commonperson__bloke',
                'blokes__person__bloke',
                'blokes__association__bloke',
                'blokes__company__bloke',
                'blokes__governmentpublic__bloke'
            ]
        }
    ],

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                labelWidth: 140,
                items: [
                    {
                        name: 'blokes__bloke',
                        fieldLabel: 'Investigado/Apontado',
                        xtype: 'rest-autocompletefield',
                        rest: 'rh.person.Restful'
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = (cfg || {});

        Ext.applyIf(
            cfg,
            {
                title: 'Filtrar por Investigado/Apontado'
            }
        );

        judicial.outcourtlawsuit.FilterBlokeWindow.superclass.constructor.call(this, cfg);
        this.readFilters();
    }
});

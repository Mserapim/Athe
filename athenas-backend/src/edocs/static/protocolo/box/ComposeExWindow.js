Ext._define('edocs.protocolo.box.ComposeExWindow', {
    extend: 'edocs.protocolo.box.ComposeWindow',

    getHomeCourtField: function(cfg) {
        if(!this._homeCourtField)
            this._homeCourtField = Ext._create('core.fields.AutocompleteField', {
                fieldLabel: 'Origem',
                name: 'home_court',
                safeMode: true,
                rest: 'rh.generalorgan.Restful',
                width: 485,
                allowBlank: false
            });

        return this._homeCourtField;
    },

    getTipoDocumentoFilter: function() {
        return [];
    },

    getExternalNumberField: function(cfg) {
        if(!this._externalField)
            this._externalField = Ext._create('Ext.form.CompositeField', {
                fieldLabel: 'Número externo',
                items: [
                    {
                        name: 'seal_number',
                        xtype: 'textfield',
                        // emptyText: 'Chancelamento do documento',
                        width: 200,
                        allowBlank: true
                    },
                    {
                        name: 'external_number',
                        xtype: 'textfield',
                        // emptyText: 'Se houver um número de protocolo externo',
                        width: 393,
                        allowBlank: true
                    }
                ]
            });

        return this._externalField;
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel) {
            this._mainPanel = edocs.protocolo.box.ComposeExWindow.superclass.getMainPanel.call(this, cfg);

            this._mainPanel.insert(
                1,
                {
                    xtype: 'container',
                    width: 875,
                    layout: {
                        type: 'hbox',
                        align: 'stretchmax'
                    },
                    items: [
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 2.75,
                            items: [
                                {
                                    xtype: 'rest-autocompletefield',
                                    fieldLabel: 'Interessado',
                                    safeMode: true,
                                    width: 485,
                                    rest: 'rh.person.Restful',
                                    name: 'interested',
                                    allowBlank: false
                                }
                            ]
                        },
                        {
                            xtype: 'container',
                            layout: 'form',
                            flex: 1.25,
                            labelWidth: 50,
                            items: [
                                {
                                    xtype: 'choicefield',
                                    fieldLabel: 'Midia',
                                    editable: false,
                                    hiddenName: 'media',
                                    width: 210,
                                    choiceId: 'protocolo.MIDIA',
                                    allowBlank: false
                                },
                            ]
                        }
                    ]
                }
            );
        }

        return this._mainPanel;
    }
});

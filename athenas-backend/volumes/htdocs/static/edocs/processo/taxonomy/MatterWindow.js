
Ext._define('edocs.processo.taxonomy.MatterWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.processo.taxonomy.MatterRestful',

    width: 900,
    height: 600,

    matter: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._matter = value;

            if(dispatch) this.observeMatter();
        }

        return this._matter;
    },

    observeMatter: function() {
        var value = this.matter();

        if(value) {
            var rest = this.getLegalMatterField().factoryRestful();
            var mask = new Ext.LoadMask(this.getEl(), {msg: 'buscando informações...'});

            mask.show();
            rest.rendererDocument(
                value,
                {
                    scope: this,
                    fn: function(document) {
                        this.getGlossaryTilePanel().setPageContent(document.glossary);
                    }
                },
                {
                    fn: function(message) {
                        Ext.Msg.show({
                            title: 'Buscando informações',
                            msg: message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                {fn: function() {
                    mask.hide();
                }}
            );
        } else {
            this.getGlossaryTilePanel().setPageContent("");
        }
    },


    getLegalMatterField: function(cfg) {
        if(!this._processLegalMatterField) {
            this._processLegalMatterField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Assunto",
                allowBlank: false,
                rest: "judicial.taxonomy.LegalMatterRestful",
                name: "legal_matter",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    allowUpdate: false,
                    allowRemove: false,
                    listeners:{
                        render: function(grid) {
                            var tbar = grid.getToolbar();
                            tbar.remove(tbar.getComponent(0)); //novo
                            tbar.remove(tbar.getComponent(0)); // editar
                            tbar.remove(tbar.getComponent(0)); // remover
                        }
                    }
                },
                comboListeners: {
                    scope: this,
                    changevalid: function(combo, value, oldvalue, valid) {
                        if(valid)
                            this.matter(value);
                        else
                            this.matter(null);
                    }
                },
                preFilter: [
                            {
                                property: 'selectable',
                                value: true,
                                stage: 100
                            },
                            {
                                property: 'administrative_classification',
                                value: true,
                                stage: 101
                            },
                            {
                                property: 'in_process_matter__process',
                                value: cfg.params.process,
                                stage: -101
                            },
                            // {
                            //     property: 'children__isnull',
                            //     value: false,
                            //     stage: -102
                            // }
                        ],
            });
        }
        return this._processLegalMatterField;
    },

    getGlossaryTilePanel: function() {
        if(!this._glossaryTilePanel)
            this._glossaryTilePanel = Ext._create('core.TilePagePanel', {
                papperModel: 'card',
            });

        return this._glossaryTilePanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                height: 600,
                items: [
                    this.getLegalMatterField(cfg),
                    {
                        xtype: "panel",
                        autoScroll: true,
                        height: 500,
                        title: "Descrição",
                        border: true,
                        items: this.getGlossaryTilePanel()
                    }
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg,
            {
                title: 'Seleção de assunto taxonômico',
                disableSaveAndNew: true
            }
        );

        edocs.processo.taxonomy.MatterWindow.superclass.constructor.call(this, cfg);
    }
});


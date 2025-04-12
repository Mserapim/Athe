Ext._define('judicial.search.Manage', {
    extend: 'toolkit.widget.TabPanel',

    getSearchGrid: function() {
        if(!this._searchGrid) {
            this._searchGrid = Ext._create('judicial.search.Grid', {
                title: 'Documentos',
                region: 'west',
                width: "45%",
                border: false,
                split: true,
                gridAutoLoad: false,
            });

            this._searchGrid.getSelectionModel().on({
                scope: this,
                rowselect: function(sm, index, data) {
                    this.partlawsuit(data.get('pk'));
                },
                rowdeselect: function() {
                    this.partlawsuit(null);
                }
            });
        }

        return this._searchGrid;
    },

    partlawsuit: function (value, observe) {
        observe = (observe === undefined ? true : observe);

        if (value !== undefined) {
            this._partlawsuit = value;
            observe && this.observePartLawsuit();
        }

        return this._partlawsuit;
    },

    observePartLawsuit: function () {
        var value = this.partlawsuit();

        if (!value) {
            this.getDisplayTilePanel().setPageContent('');
            this.getDisplayTilePanel().disable();
            return;
        }

        // Início do trecho referente ao tile
        var mask = new Ext.LoadMask(
            this.getDisplayTilePanel().getEl(), {
            msg: 'Buscando documento...'
        }
        );
        mask.show();

        var tile = this.getDisplayTilePanel();
        var rest = Ext._create('judicial.PartLawsuitRestful');

        rest.doRequest(
            rest.getRoute('read_render', null, 'GET', {
                params: { pk: value },
                success: function (xhr) {
                    var rst = Ext.decode(xhr.responseText);

                    if (rst.success) {
                        tile.enable();
                        tile.extraClasses = (rst.unfolded ? ['unfolded'] : []);
                        tile.setPageContent(rst.content);
                        (rst.extra_pages || []).forEach(
                            function (page) {
                                tile.addPageContent(page);
                            }
                        );
                    } else {
                        Ext.Msg.show({
                            title: 'Carregando',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                failure: function () {
                    Ext.Msg.show({
                        title: 'Carregando',
                        msg: 'Recurso indisponivel no momento.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                callback: function () {
                    mask.hide();
                }
            })
        );
    },

    getDisplayTilePanel: function () {
        if (!this._displayTilePanel) {
            this._displayTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                region: 'center',
                split: true,
                width: 125
            });
        }

        // this._displayTilePanel.setPageContent('<h3>Informe um termo para busca</h3>');

        return this._displayTilePanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Pesquisa em Documentos',
                layout: 'border',
                items: [
                    this.getSearchGrid(),
                    this.getDisplayTilePanel(),
                ],
                border: false,
            }
        );

        judicial.search.Manage.superclass.constructor.call(this, cfg);
    }
});

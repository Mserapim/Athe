var NFS_SYNC_TIMELAPSE = 5000;

Ext._define('judicial.proccess.BaseWorkspace', {
    extend: 'Ext.Viewport',

    getHeaderPage: function(cfg) {
        if(!this._headerPage) {
            var wndConfig = cfg.windowConfig();
            this._headerPage = Ext._create('Ext.Container', {
                region: 'north',
                html: '',
                height: 45,
                minHeight: 45,
                maxHeight: 45,
                split: true,
                autoEl: 'div',
                cls: 'base no-print',
                tpl: [
                    '<div>',
                        '<div class="header left">{cache_number} - {title}</div>',
                        '<div class="header right">{location_unicode}</div>',
                    '</div>'
                ],
                data: wndConfig
            });
        }

        return this._headerPage;
    },

    getCoverPanel: function(cfg) {
      if (!this._coverPanel) {
          var wndConfig = cfg.windowConfig();

          this._coverPanel = Ext._create('Ext.Panel', {
              title: 'Capa - ' + wndConfig.cache_number,
              layout: 'fit',
              temporary: false,
              items: this.getTileCoverLawsuit(cfg),
              tbar: [
                {
                    text: 'Interessados',
                    tooltip: {
                        title: 'Interessados',
                        text: 'Gerenciar os interessados do procedimento.'
                    },
                    handler: this.openInterested,
                    iconCls: 'icon-judicial icon-ejud-glosary-investigation',
                    scope: this
                },
                '-',
                {
                    text: 'Investigados',
                    tooltip: {
                        title: 'Investigados',
                        text: 'Gerenciar os investigados do procedimento.'
                    },
                    handler: this.openBloke,
                    scope: this,
                    iconCls: 'icon-judicial icon-ejud-part-invstigation'
                },
                '-',
                '->',
                '-',
                {
                    text: 'Marcadores estatisticos',
                    tooltip: {
                        title: 'Marcadores estatisticos',
                        text: 'Gerenciar os marcadores estatisticos do procedimento.'
                    },
                    scope: this,
                    handler: function() {
                        Ext._create('judicial.statisticMarker.OutCourtLawsuitManage', {
                            modal: true,
                            selected: [wndConfig.pk]
                        }).show();
                    },
                    scope: this,
                    iconCls: 'icon-judicial icon-ejud-part-invstigation'
                }
            ]
          });

          this._coverPanel.on({
              afterrender: function(panel) {
                  const dm = Ext._create('judicial.reminder.lawsuit.DisplayManage', {
                      lawsuitId: wndConfig.pk,
                      paddingTop: 85,
                      attached: panel
                  });

                  setTimeout(function () { dm.start() }, 300);
              }
          })
      }

      return this._coverPanel;
    },

    getContentPanel: function(cfg) {
        if(!this._contentPanel){
            this._contentPanel = Ext._create('Ext.TabPanel', {
                region: 'center',
                activeTab: 0,
                minTabWidth: 120,
                tabWidth: 120,
                flex: 1,
                enableTabScroll: true,
                items: [
                    this.getCoverPanel(cfg)
                ]
            });
        }

        return this._contentPanel;
    },

    openInterested: function() {
        Ext._create('Ext.Window', {
            modal: true,
            width: 750,
            height: 500,
            title:'Gerenciamento de Interessados',
            items: this._factoryGridInterested()
        }).show();
    },

    _factoryGridInterested: function(){
        var gridInterested = Ext._create('judicial.interested.Grid', {
            height: 450,
            gridAutoLoad: false
        });

        gridInterested.setParam('lawsuit', this._wndCfg.pk);
        gridInterested.setFilterProperty('lawsuit', this._wndCfg.pk, 1001);
        gridInterested.getStore().load();

        return gridInterested;
    },

    openBloke: function() {
        Ext._create('Ext.Window', {
            modal: true,
            width: 750,
            height: 500,
            title:'Gerenciamento de Investigados',
            items: this._factoryGridBloke()
        }).show();
    },

    _factoryGridBloke: function() {
        var gridBloke = Ext._create('judicial.bloke.Grid', {
            height: 450,
            gridAutoLoad: false
        });

        gridBloke.setParam('lawsuit', this._wndCfg.pk);
        gridBloke.setFilterProperty('lawsuit', this._wndCfg.pk, 1001);
        gridBloke.getStore().load();

        return gridBloke;
    },

    loadLawsuitCover: function(lawsuitId, location) {
        var rest = Ext._create('judicial.OutCourtLawsuitRestful');

        rest.doRequest(
            rest.getRoute('cover', false, 'GET', {
                params: {
                    pk: lawsuitId,
                    execution_organ: location
                },
                scope: this,
                callback: function() {},
                success: function(xhr) {
                    this.getTileCoverLawsuit().setPageContent(xhr.responseText);
                },
                failure: function() {
                    this.getTileCoverLawsuit().setPageContent('Ocorreu um erro buscando inforações.');
                }
            })
        );
    },

    getTileCoverLawsuit: function(cfg) {
        if(!this._tileCoverPagePanel){
            var wndConfig = cfg.windowConfig();
            this._tileCoverPagePanel =  Ext._create('core.TilePagePanel', {});

            this._tileCoverPagePanel.on({
                scope: this,
                afterrender: function(panel) {
                    this.loadLawsuitCover(wndConfig.pk, wndConfig.location);
                }
            });
        }
        return this._tileCoverPagePanel;
    },

    partLawsuit: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._partLawsuit = value;

            if(dispatch)
                this.partLawsuitObserve();
        }

        return this._partLawsuit;
    },

    readPartLawsuitToTilePanel: function(partLawsuit, panel) {
        var rest = Ext._create('judicial.PartLawsuitRestful');
        var tile = Ext._create('core.TilePagePanel', {});
        var pk = partLawsuit.get('pk');

        tile.on({
            scope: this,
            render: function(tile) {
                var mask = new Ext.LoadMask(tile.getEl(), { msg: 'carregando informações...' });
                mask.show();
                rest.doRequest(
                    rest.getRoute('read_render', null, 'GET', {
                        params: { pk: pk },
                        success: function(xhr) {
                            var rst = Ext.decode(xhr.responseText);

                            if (rst.success) {
                                tile.extraClasses = (rst.unfolded ? ['unfolded'] : []);
                                tile.setPageContent(rst.content);
                                (rst.extra_pages || []).forEach(
                                    function(page) {
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
                        failure: function() {
                            Ext.Msg.show({
                                title: 'Carregando',
                                msg: 'Recurso indisponivel no momento.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK
                            });
                        },
                        callback: function() {
                            mask.hide();
                        }
                    })
                );

                panel.on({
                    beforeremove: function (p, c) {
                        if (c.dm === tile.dm) {
                            c.dm.destroy();
                            c.dm = undefined;
                        }
                    }
                });

                tile.dm = Ext._create('judicial.reminder.partlawsuit.DisplayManage', {
                    partLawsuitId: partLawsuit.get('pk'),
                    paddingTop: 85,
                    attached: panel
                });

                setTimeout(function () { tile.dm.start(); }, 300);
            }
        });

        panel.add(tile);
        panel.doLayout();
    },

    readPartLawsuit: function(partLawsuit, panel) {
        if (partLawsuit.get('signed_by') !== null && ((localStorage.getItem('eextForceHTML') || null) === null)) {
            this.readPartLawsuitToPDFView(partLawsuit, panel);
        } else {
            this.readPartLawsuitToTilePanel(partLawsuit, panel);
        }
    },

    openContentPanel: function(partLawsuit, temporary) {
        var panel = Ext._create('Ext.Panel', {
            title: partLawsuit.get('unicode'),
            closable: true,
            layout: 'fit',
            height: this.getContentPanel().getBox().height,
            temporary: temporary
        });

        this.readPartLawsuit(partLawsuit, panel);
        this.getContentPanel().add(panel);
        this.getContentPanel().activate(panel);
    },

    refreshContentPanel: function(partLawsuit, panel, temporary) {
        panel.setTitle(partLawsuit.get('unicode'));
        this.getContentPanel().activate(panel);
        panel.removeAll();
        this.readPartLawsuit(partLawsuit, panel);
        panel.doLayout();
    },

    readPartLawsuitToPDFView: function(partLawsuit, panel) {
        var urlPDF = Ext._create('judicial.PartLawsuitRestful')
            .getRoute('read_pdf', partLawsuit.get('pk'), 'GET').url;

        var pdfView = Ext._create('Ext.Container', {
            autoEl: 'div',
            html: '<embed src="' + urlPDF + '" style="width: 100%; height: 100%; border: none" id="' + Ext.id() + '" type="application/pdf" />',
            listeners: {
                scope: this,
                render: function(container) {
                    var RemoteObserver = core.RemoteObserver;

                    var cb = RemoteObserver.on('judicial-load-cache-doc', {
                        scope: this,
                        fn: function(result) {
                          var self = this;
                          if(result.part_id === partLawsuit.get('pk')){
                              // Este atraso serve para contornar a questao do nfs
                                setTimeout(
                                    function() {
                                        self.refreshContentPanel(partLawsuit, panel);
                                    },
                                    NFS_SYNC_TIMELAPSE
                                );
                          }
                        }
                    });

                    panel.on({
                        beforeremove: function(p, c) {
                            if (c.dm === container.dm) {
                                c.dm.destroy();
                                c.dm = undefined;
                            }
                        }
                    });

                    container.dm = Ext._create('judicial.reminder.partlawsuit.DisplayManage', {
                        partLawsuitId: partLawsuit.get('pk'),
                        paddingTop: 85,
                        attached: panel,
                        callback: {
                            afterNew: {
                                scope: this,
                                fn: function() {
                                    this.getPartLawsuitGrid().getStore().reload();
                                }
                            },
                            afterChanges: {
                                scope: this,
                                fn: function() {
                                    this.getPartLawsuitGrid().getStore().reload();
                                }
                            }
                        }
                    });

                    setTimeout(function () { container.dm.start(); }, 300);
                }
            }
        });

        panel.add(pdfView);
    },

    partLawsuitObserve: function() {
        var value = this.partLawsuit();
        var activePanel = this.getContentPanel().getActiveTab();

        if(value && activePanel.temporary) {
            this.refreshContentPanel(value, activePanel, true);
        } else if(value && !activePanel.temporary) {
            this.openContentPanel(value, true)
        }
    },

    _headePanelOrientationConfig: function() {
        return {};
    },

    getHeaderPanel: function(cfg) {
        if(!this._headerPanel) {
            var initConfig = {
                html: '',
                height: 45,
                autoEl: 'div',
                cls: 'base no-print',
                tpl: [
                    '<div>',
                        '<div class="header left">{cache_number} - {title}</div>',
                        '<div class="header right">{location_unicode}</div>',
                    '</div>'
                ],
                data: cfg.windowConfig()
            };

            Ext.apply(initConfig, this._headePanelOrientationConfig());

            this._headerPanel = Ext._create('Ext.Container', initConfig);
        }

        return this._headerPanel;
    },

    _partLawsuitOrientationConfig: function() {
        return {}
    },

    _signSelected: function(selected) {
        var rest = Ext._create(judicial.PartLawsuitGrid.getClassByPath(selected.get('path'))).factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'assinado...' });

        mask.show();
        rest.doRequest(
            rest.getRoute('sign', selected.get('pk'), 'PUT', {
                scope: this,
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    rst = Ext.decode(xhr.responseText);

                    if(rst.success) {
                        var self = this;
                        var store = this.getPartLawsuitGrid().getStore();

                        store.reload({
                            callback: function() {
                                var at = store.findBy(function(record) {
                                    return record.get('pk') === selected.get('pk');
                                });

                                if (at >= 0) {
                                    var record = store.getAt(at);
                                    self.partLawsuit(record);
                                }
                            }
                        });
                    } else {
                        Ext.Msg.show({
                            title: 'Assinando',
                            msg: rst.message,
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Assinando',
                        msg: 'Recurso indisponivel no momento, tente novamente mais tarde.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            })
        );
    },

    signSelected: function() {
        var selection = this.getPartLawsuitGrid().getSelectionModel().getSelections();

        if (selection.length > 0) {
            var selected = selection[0];

            Ext.Msg.show({
                title: 'Assinando',
                msg: 'Tem certeza que deseja assianar o documento <b>"' + selected.get('unicode') + '"</b>?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if (btn === 'no') return;
                    this._signSelected(selected);
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Assinando',
                msg: 'Primeiro selecione o item que deseja assinar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    rebuildCache: function() {
        var selection = this.getPartLawsuitGrid().getSelectionModel().getSelections();

        if (selection.length > 0) {
            var selected = selection[0];

            Ext.Msg.show({
                title: 'Recriando PDF do Documento',
                msg: 'Tem certeza que deseja recriar o documento <b>"' + selected.get('unicode') + '"</b>?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if (btn === 'no') return;
                    this._rebuildCache(selected);
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Recriando PDF do Documento',
                msg: 'Primeiro selecione o item que deseja recriar.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    _rebuildCache: function(selected) {
        var rest = Ext._create('judicial.PartLawsuitRestful');
        var mask = new Ext.LoadMask(this.getEl(), { msg: 'Criando documento...' });

        mask.show();
        rest.doRequest(
            rest.getRoute('rebuild_cache_doc', false, 'PUT', {
                scope: this,
                params: {
                    pk: selected.get('pk')
                },
                callback: function() {
                    mask.hide();
                },
                success: function(xhr) {
                    rst = Ext.decode(xhr.responseText);
                    Ext.Msg.show({
                        title: 'Recriando arquivo',
                        msg: rst.message,
                        icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                failure: function() {
                    Ext.Msg.show({
                        title: 'Recriando arquivo',
                        msg: 'Recurso indisponivel no momento, tente novamente mais tarde.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            })
        );
    },

    createContextMenu: function(record) {
        var signedBy = record.get('signed_by');
        var isPublic = record.get('is_public');
        var pk = record.get('pk');
        var urlCache = record.get('abs_url_cache');

        return Ext._create('Ext.menu.Menu', {
            items: [
                {
                    text: 'Abrir em outra janela',
                    disabled: signedBy === null,
                    handler: function() {
                        window.open(urlCache, '_blank')
                    }
                },
                {
                    text: 'Abrir em outra aba',
                    disabled: signedBy === null,
                    scope: this,
                    handler: function() {
                        this.openContentPanel(record);
                    }
                },
                {
                    text: (signedBy ? 'Fazer o download do arquivo' : 'Imprimir para arquivo'),
                    scope: this,
                    handler: function() {
                        if (signedBy) {
                            window.open(urlCache + '?force_download=on', '_blank')
                        } else {
                            this.getPartLawsuitGrid().printerDocument();
                        }
                    }
                },
                {
                    text: 'Gerar documento novamente',
                    disabled: (signedBy === null || this.adminMode === false),
                    scope: this,
                    handler: function() {
                        this.rebuildCache();
                    }
                },
                '-',
                {
                    text: 'Assinar este documento',
                    disabled: signedBy !== null,
                    scope: this,
                    handler: function() {
                        this.signSelected();
                    }
                },
                // TODO: Implementar a funcionalidade listadas abaixo.
                // {
                //     text: 'Pedir pre-analise'
                // },
                // isPublic ?
                //     {
                //         text: 'Tornar documento restrito'
                //     } :
                //     {
                //         text: 'Tornar documento público'
                //     }
            ]
        });
    },

    getPartLawsuitGrid: function(cfg) {
        if(!this._partLawsuitGrid) {
            var wndConfig = cfg.windowConfig();
            var initConfig = {
                title: 'Eventos',
                collapsible: true,
                cls: 'base no-print',
                columnAction: false,
                toolbarHideLabel: true,
                configOrderToolBar: [
                    'add', 'edit', 'remove', '-',
                    'publish', 'workerReminder',
                    'bookmarker', '-', 'downloadLawsuit',
                    'requestCollaboration', '-', 'sendSecretary',
                    '-', 'removeSecretary',
                    '-', '->'
                ],
                adminMode: cfg.adminMode,
                viewConfig: {
                    getRowClass: function(record) {
                        console.log('thunder');
                        var classes = ['grid-line-height-150'];

                        if(record.get('unfolded_by') !== null)
                            classes.push('dashed');

                        if(window.config().pk !== record.get('lawsuit'))
                            classes.push('lawsuit-connected');

                        return classes.join(' ');
                    }
                }
            };

            if (cfg.mode == "historic") {
                initConfig['configOrderToolBar'] = []
            }

            Ext.apply(initConfig, this._partLawsuitOrientationConfig());

            this._partLawsuitGrid = Ext._create('judicial.PartLawsuitGrid', initConfig);

            this._partLawsuitGrid.setSortProperty('page_number', 'DESC', false);

            this._partLawsuitGrid.setParam('lawsuit', wndConfig.pk);
            this._partLawsuitGrid.setParam('location', wndConfig.location);
            this._partLawsuitGrid.setFilterProperty('lawsuit', wndConfig.pk, 100, false);
            this._partLawsuitGrid.setFilterProperty('shared_with_lawsuit', wndConfig.pk, 100, false);
            this._partLawsuitGrid.setFilterProperty('unfolded_by__isnull', false, -100);

            this._partLawsuitGrid.on({
                scope: this,
                rowcontextmenu: function(grid, rowIndex, event) {
                    event.preventDefault();
                    this.preventChange = true;

                    var record = grid.getStore().getAt(rowIndex);
                    var menu = this.createContextMenu(record);

                    grid.getSelectionModel().selectRow(rowIndex);
                    menu.showAt(event.xy);
                }
            });

            this._partLawsuitGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(model) {
                    var selection = model.getSelections();
                    var self = this;

                    if (!self.preventChange) {
                        if(selection.length > 0) {
                            setTimeout(
                                function() {
                                    self.preventChange = false;
                                    self.partLawsuit(selection[0]);
                                },
                                500
                            );
                        } else {
                            setTimeout(
                                function() {
                                    self.preventChange = false;
                                    self.partLawsuit(null);
                                },
                                500
                            );
                        }
                    } else {
                        setTimeout(
                            function() {
                                self.preventChange = false;
                            },
                            500
                        );
                    }
                }
            });
        }

        return this._partLawsuitGrid;
    },

    updateInformations: function(data) {
    },

    constructor: function(cfg) {

        cfg = cfg || {};
        Ext.apply(cfg, {
            layout: 'border',
            items: [
                this.getHeaderPage(cfg),
                this.getPartLawsuitGrid(cfg),
                this.getContentPanel(cfg),
            ]
        });

        judicial.proccess.BaseWorkspace.superclass.constructor.call(this, cfg);

        if(!this._wndCfg)
            this._wndCfg = cfg.windowConfig();

        var RemoteObserver = core.RemoteObserver;

        var cb = RemoteObserver.on('judicial-load-cache-lawsuit', {
            scope: this,
            fn: function(result) {
                // para sincronização dentro do NFS
                setTimeout(
                    function() {
                        window.open(result.url_cache);
                    },
                    NFS_SYNC_TIMELAPSE
                )
            }
        });
    }
});

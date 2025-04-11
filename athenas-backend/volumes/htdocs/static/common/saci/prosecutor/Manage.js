
Ext._define('common.saci.prosecutor.Manage', {
    extend: 'toolkit.widget.TabPanel',

    calculateBoxPanelWidth: function() {
        var width = (Ext.getBody().getBox().width - 900);
        return (width > 525 ? width : 525);
    },

    getPersonGrid: function() {
        if(!this._personGrid){
            this._personGrid = Ext._create('common.internalSecurity.person.Grid', {
                title: 'Cadastro',
                hideItemsToolbar: ['remove', 'download'],
                keywordFieldWidth: this.calculateBoxPanelWidth() - 300,
                columnAction: false,
                gridAutoLoad: true,
                allowRemove: false,
                height: 300,
                safeMode: true,
                filterNewMenu: function(item) {
                    var allowed = ['pessoafisica', 'pessoajuridica', 'advogadosimplificado'];
                    return (allowed.indexOf(item.name) >= 0);
                }
            });

            this._personGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    if(selm.getSelections().length > 0)
                        this.person(selm.getSelections()[0].get('pk'));
                    else
                        this.person(null);
                }
            });

            this._personGrid.on({
                scope: this,
                resize: function (grid, adjWidth) {
                    grid.getKeywordField().setWidth(adjWidth - 380);
                },
            });
        }
        return this._personGrid;
    },

    getPersonQueueGrid: function() {
        if(!this._personQueueGrid) {
            this._personQueueGrid = Ext._create('common.saci.queue.PersonGrid', {
                title: 'Aguardando atendimento',
                hideItemsToolbar: ['person', '-', 'edit', 'remove', '-', 'search', 'download'],
                columnAction: false,
                gridAutoLoad: true,
                allowRemove: false,
                height: 300,
                safeMode: true
            });

            this._personQueueGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(selm) {
                    if(selm.getSelections().length > 0)
                        this.person(selm.getSelections()[0].get('pk'));
                    else
                        this.person(null);
                }
            });
        }
        return this._personQueueGrid;
    },

    person: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._person = value;

            if(dispatch)
                this.observePerson();
        }

        return this._person;
    },

    observePerson: function() {
        var value = this.person();

        if(value) {
            this.getAttendanceTab().setActiveTab(0);

            this.getAttendanceOpenedGrid().enable();
            this.getAttendanceOpenedGrid().setParam('person', value);
            this.getAttendanceOpenedGrid().setFilterProperty('signed_by__isnull', true, 99);
            this.getAttendanceOpenedGrid().setFilterProperty('person', value, 100);
            this.getAttendanceOpenedGrid().setFilterProperty('represented', value, 100);

            this.getAttendanceClosedGrid().enable();
            this.getAttendanceClosedGrid().setParam('person', value);
            this.getAttendanceClosedGrid().setFilterProperty('person', value, 100);
            this.getAttendanceClosedGrid().setFilterProperty('represented', value, 100);

        }

        else {

            this.getAttendanceOpenedGrid().disable();

            this.getAttendanceOpenedGrid().setParam('person', 0);
            this.getAttendanceOpenedGrid().setFilterProperty('signed_by__isnull', false, 99, false);
            this.getAttendanceOpenedGrid().setFilterProperty('person', 0, 100, false);
            this.getAttendanceOpenedGrid().setFilterProperty('represented', 0, 100, false);
            this.getAttendanceOpenedGrid().getStore().removeAll();


            this.getAttendanceClosedGrid().disable();
            this.getAttendanceClosedGrid().setParam('person', 0);
            this.getAttendanceClosedGrid().setFilterProperty('person', 0, 100, false);
            this.getAttendanceClosedGrid().setFilterProperty('represented', 0, 100, false);

            this.getAttendanceClosedGrid().getStore().removeAll();
        }
    },

    getAttendanceOpenedGrid: function() {
        if(!this._attendanceOpenedGrid) {
            this._attendanceOpenedGrid = Ext._create('common.saci.prosecutor.Grid', {
                title: 'Atendimento',
                hideItemsToolbar: ['print', 'download'],
                toolbarHideLabel: true,
                columnAction: false,
                gridAutoLoad: false,
            });

            this._attendanceOpenedGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0)
                        this.attendance({
                            pk: selection[0].get('pk'),
                            grid: this.getAttendanceOpenedGrid()
                        });
                    else
                        this.attendance(null);
                }
            });

            this._attendanceOpenedGrid.getStore().on({
                scope: this,
                load: function(store) {
                    var selected = this._attendanceOpenedGrid.getSelectionModel().getSelected();
                    if(selected)
                        this.attendance({
                            pk: selected.get('pk'),
                            grid: this.getAttendanceOpenedGrid()
                        });
                    else
                        this.attendance(null);
                }
            });
        }

        return this._attendanceOpenedGrid;
    },

    getAttendanceClosedGrid: function() {
        if(!this._attendanceClosedGrid) {
            this._attendanceClosedGrid = Ext._create('common.saci.attendance.Grid', {
                title: 'Atendimentos encaminhados',
                configOrderToolBar: ['search','historic','-','print','-'],
                toolbarHideLabel: true,
                columnAction: false,
                gridAutoLoad: false,
                doubleClickHandler: function() {}
            });

            this._attendanceClosedGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sm) {
                    var selection = sm.getSelections();
                    if(selection.length > 0) {
                        this.attendance({
                            pk: selection[0].get('pk'),
                            grid: this.getAttendanceClosedGrid()
                        });
                    }
                    else
                        this.attendance(null);
                }
            });
        }

        return this._attendanceClosedGrid;
    },

    attendance: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._attendance = value;

            if(dispatch)
                this.observeAttendance();
        }

        return this._attendance;
    },

    readPageContent: function(pk) {
        tile = this.getFeedbackDisplayTilePanel();

        if ( !tile.mask )
            tile.mask = new Ext.LoadMask(tile.getEl(), 'carregando informações...');

        if(tile._readRenderTID)
            Ext.Ajax.abort(tile._readRenderTID);

        tile.mask.show();
        tile.setPageContent('<p>Carregando conteúdo...</p>');
        tile._readRenderTID = Ext.Ajax.request({
            url: core.callAction('SACIAttendanceRestful', 'read_render'),
            params: {pk: pk},
            method: 'GET',
            callback: function() {
                tile._readRenderTID = null;
                tile.mask.hide();
            },
            success: function(xhr) {
                var rst = Ext.decode(xhr.responseText);

                if(rst.success) {
                    tile.setPageContent(rst.content);
                    (rst.extra_pages || []).forEach(
                        function(page) {
                            tile.addPageContent(page);
                        }
                    );
                }
                else
                    tile.setPageContent([
                        '<p>Ocorreu um erro carregando o documento.</p>',
                        '<p>Mensagem: ' + rst.message + '</p>'
                    ].join(''));
            },
            failure: function(xhr) {
                tile.setPageContent('<p>Erro carregando informações do documento.</p>');
            }
        });
    },

    observeAttendance: function() {
        var value = this.attendance();

        if(value) {
            this.readPageContent(value.pk);
        }
    },

    getFeedbackDisplayTilePanel: function(cfg) {
        if(!this._feedbackDisplayTilePanel)
            this._feedbackDisplayTilePanel = Ext._create('core.TilePagePanel', {
                region: 'center',
            });

        return this._feedbackDisplayTilePanel;
    },

    getAttendanceTab: function() {
        if(!this._attendanceTab) {
            this._attendanceTab = Ext._create('Ext.TabPanel', {
                region: 'center',
                activeTab: 0,
                tabPosition: 'top',
                border: false,
                items: [
                    this.getAttendanceOpenedGrid(),
                    this.getAttendanceClosedGrid()
                ]
            });
        }

        return this._attendanceTab;
    },

    getPersonTab: function() {
        if(!this._personTab) {
            this._personTab = Ext._create('Ext.TabPanel', {
                region: 'north',
                activeTab: 0,
                tabPosition: 'top',
                border: false,
                items: [
                    this.getPersonQueueGrid(),
                    this.getPersonGrid()
                ]
            });
        }

        return this._personTab;
    },

    getPersonAttendancePanel: function() {
        if(!this._personAttendancePanel)
            this._personAttendancePanel = Ext._create('Ext.Panel', {
                region: 'west',
                border: false,
                split: true,
                layout: 'border',
                items: [
                    this.getPersonTab(),
                    this.getAttendanceTab()
                ]
            });

        return this._personAttendancePanel;
    },

    _resizeEvent: function (panel, adjWidth) {
        toolkit.util.updateGridAndTileDimensions({
            target: this.getPersonAttendancePanel(),
            containerWidth: adjWidth,
        });
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Gestor de Atendimentos',
        });

        Ext.apply(cfg, {
            layout: 'border',
            items: [
                this.getPersonAttendancePanel(),
                this.getFeedbackDisplayTilePanel(cfg)
            ],
            listeners: {
                scope: this,
                resize: this._resizeEvent,
            },
        });

        common.saci.prosecutor.Manage.superclass.constructor.call(this, cfg);

        this.observePerson();
    }
});

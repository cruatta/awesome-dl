import React from 'react';
import Drawer from '@material-ui/core/Drawer';
import List from '@material-ui/core/List';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import { Settings } from './settings'
import AppBar from "@material-ui/core/AppBar";
import {IconButton, Toolbar} from "@material-ui/core";
import MenuIcon from "@material-ui/icons/Menu";
import Typography from "@material-ui/core/Typography";
import {createStyles, makeStyles, Theme} from "@material-ui/core/styles";

const useStyles = makeStyles((theme: Theme) =>
    createStyles({
        root: {
            flexGrow: 1,
        },
        menuButton: {
            marginRight: theme.spacing(2),
        },
        title: {
            flexGrow: 1,
        },
    }),
);


export const SettingsView: React.FC = () => {
    const [state, setState] = React.useState({
        visible: false,
    });

    const toggleDrawer = (open: boolean) => (
        event: React.KeyboardEvent | React.MouseEvent,
    ) => {
        if (
            event.type === 'keydown' &&
            ((event as React.KeyboardEvent).key === 'Tab' ||
                (event as React.KeyboardEvent).key === 'Shift')
        ) {
            return;
        }

        setState({ visible: open } );
    };

    const classes = useStyles();
    const settings = () => (
        <div
            role="presentation"
        >
            <List>
                <ListItem>
                    <Settings />
                </ListItem>
            </List>
            <Divider />
        </div>
    );

    return (
        <AppBar position="static">
            <Toolbar>
                <IconButton edge="start" className={classes.menuButton} color="inherit" aria-label="menu">
                    <MenuIcon onClick={toggleDrawer(true)} />
                </IconButton>
                <Typography variant="h6" className={classes.title}>
                    AwesomeDL
                </Typography>
            </Toolbar>
            <div>
                <React.Fragment>
                    <Drawer anchor='left' open={state['visible']} onClose={toggleDrawer(false)}>
                        {settings()}
                    </Drawer>
                </React.Fragment>
            </div>
        </AppBar>
    );
}
import React from 'react';
import User from './User'
import styled from 'styled-components'
import {List, Skeleton} from 'antd';

const StyledHeader = styled.div`
  font-family: Open Sans, sans-serif;
  font-style: normal;
  font-weight: 600;
  font-size: 1.25em;
  line-height: 1.7em;
  color: rgba(0, 0, 0, 0.5);
  margin-bottom: 0.2em;
`

const UserList = (props) => (
  <>
    <StyledHeader>{props.header}</StyledHeader>
    <List
      className="user-list"
      itemLayout="horizontal"
      dataSource={props.users}
      renderItem={ user => (

        <List.Item style={{border: 'none'}}>
          <Skeleton avatar title={false} loading={props.loading} active>
            <User 
              name = {user['profile']['username']}
              image = {user['profile']['image']}
              username = {user['profile']['username']}
              following = {user['profile']['following']}
              hasButton = {true}
            />
          </Skeleton>
        </List.Item>
      )}
    />
  </>
)

export default UserList